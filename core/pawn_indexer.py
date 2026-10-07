# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------------------------------------
#   Pawn project indexer for Spawn IDE.
#   This module implements a Pawn-specific parser, preprocessor, include graph
#   and SQLite-backed symbol cache. It does not depend on Universal Ctags.
# -------------------------------------------------------------------------------------------------------------------

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from core.logger import SpawnLogger
from core.platform_utils import PlatformUtils


_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_INCLUDE_RE = re.compile(
    r"^\s*#\s*(tryinclude|include)\s*([<\"])([^>\"]+)[>\"]",
    re.IGNORECASE,
)
_DEFINE_RE = re.compile(
    r"^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s*\(([^)]*)\))?(?:\s+(.*))?$",
    re.IGNORECASE,
)
_UNDEF_RE = re.compile(r"^\s*#\s*undef\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)
_PRAGMA_ONCE_RE = re.compile(r"^\s*#\s*pragma\s+once\b", re.IGNORECASE)
_ENDINPUT_RE = re.compile(r"^\s*#\s*endinput\b", re.IGNORECASE)
_IF_RE = re.compile(r"^\s*#\s*if\s+(.+?)\s*$", re.IGNORECASE)
_IFDEF_RE = re.compile(r"^\s*#\s*ifdef\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)
_IFNDEF_RE = re.compile(r"^\s*#\s*ifndef\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)
_ELSEIF_RE = re.compile(r"^\s*#\s*elseif\s+(.+?)\s*$", re.IGNORECASE)
_ELSE_RE = re.compile(r"^\s*#\s*else\b", re.IGNORECASE)
_ENDIF_RE = re.compile(r"^\s*#\s*endif\b", re.IGNORECASE)

_FUNCTION_PREFIX_RE = re.compile(
    r"^\s*(?:(public|stock|native|forward|hook)\s+)?"
    r"(?:(\w+)\s*:\s*)?"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*\(",
    re.IGNORECASE,
)
_COMMAND_RE = re.compile(r"^\s*(CMD|YCMD|ACMD)\s*:\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.IGNORECASE)
_DEFINE_SYMBOL_RE = re.compile(
    r"^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE
)
_TYPEDEF_RE = re.compile(
    r"^\s*typedef\s+.*?\b([A-Za-z_][A-Za-z0-9_]*)\s*;\s*$", re.IGNORECASE
)
_ENUM_RE = re.compile(
    r"^\s*enum(?:\s+([A-Za-z_][A-Za-z0-9_]*))?\s*(?:\{|$)", re.IGNORECASE
)
_DECL_RE = re.compile(
    r"^\s*(new|static|const|decl)\b(.*)$", re.IGNORECASE
)
_CONTROL_NAMES = {
    "if", "else", "for", "while", "do", "switch", "case", "sizeof", "state",
    "return", "assert", "native", "forward", "public", "stock", "switch"
}
_PAWN_KEYWORDS = {
    "new", "static", "const", "decl", "public", "stock", "native", "forward",
    "enum", "if", "else", "for", "while", "do", "switch", "case", "default",
    "return", "break", "continue", "sizeof", "state", "goto", "char", "bool",
    "true", "false", "Float", "view_as", "tagof", "defined"
}


@dataclass(frozen=True)
class PawnSymbol:
    name: str
    kind: str
    line: int
    column: int
    scope_start: int = 0
    scope_end: int = 0
    signature: str = ""
    detail: str = ""
    local: bool = False


@dataclass(frozen=True)
class PawnInclude:
    source_path: str
    line: int
    include_name: str
    target_path: Optional[str]
    required: bool


@dataclass
class ParsedFile:
    path: str
    fingerprint: str
    symbols: List[PawnSymbol]
    includes: List[PawnInclude]
    pragma_once: bool = False


class _ExpressionParser:
    """Small deterministic evaluator for Pawn #if expressions."""

    TOKEN_RE = re.compile(
        r"\s*(?:(0[xX][0-9A-Fa-f]+|\d+)|"
        r"([A-Za-z_][A-Za-z0-9_]*)|"
        r"(==|!=|<=|>=|&&|\|\||<<|>>|[()+\-*/%<>&|^!~]))"
    )

    def __init__(self, expr: str, macros: Dict[str, str]):
        self.tokens: List[Tuple[str, str]] = []
        self.index = 0
        self.macros = macros
        pos = 0
        while pos < len(expr):
            match = self.TOKEN_RE.match(expr, pos)
            if not match:
                break
            if match.group(1):
                self.tokens.append(("number", match.group(1)))
            elif match.group(2):
                self.tokens.append(("ident", match.group(2)))
            else:
                self.tokens.append(("op", match.group(3)))
            pos = match.end()

    def _peek(self) -> Optional[str]:
        return self.tokens[self.index][1] if self.index < len(self.tokens) else None

    def _take(self) -> Optional[str]:
        if self.index >= len(self.tokens):
            return None
        value = self.tokens[self.index][1]
        self.index += 1
        return value

    def _macro_number(self, name: str, seen: Optional[Set[str]] = None) -> int:
        seen = set() if seen is None else seen
        if name in seen:
            return 0
        seen.add(name)
        value = self.macros.get(name)
        if value is None:
            return 0
        value = value.strip()
        if not value:
            return 1
        if value.lower().startswith("0x"):
            try:
                return int(value, 16)
            except ValueError:
                return 0
        try:
            return int(value, 0)
        except ValueError:
            if _IDENTIFIER_RE.fullmatch(value):
                return self._macro_number(value, seen)
            return 1

    def parse(self) -> int:
        value = self._parse_or()
        return int(value)

    def _parse_or(self) -> int:
        value = self._parse_and()
        while self._peek() == "||":
            self._take()
            rhs = self._parse_and()
            value = 1 if value or rhs else 0
        return value

    def _parse_and(self) -> int:
        value = self._parse_bitor()
        while self._peek() == "&&":
            self._take()
            rhs = self._parse_bitor()
            value = 1 if value and rhs else 0
        return value

    def _parse_bitor(self) -> int:
        value = self._parse_bitxor()
        while self._peek() == "|":
            self._take()
            value |= self._parse_bitxor()
        return value

    def _parse_bitxor(self) -> int:
        value = self._parse_bitand()
        while self._peek() == "^":
            self._take()
            value ^= self._parse_bitand()
        return value

    def _parse_bitand(self) -> int:
        value = self._parse_equality()
        while self._peek() == "&":
            self._take()
            value &= self._parse_equality()
        return value

    def _parse_equality(self) -> int:
        value = self._parse_relational()
        while self._peek() in ("==", "!="):
            op = self._take()
            rhs = self._parse_relational()
            value = int(value == rhs) if op == "==" else int(value != rhs)
        return value

    def _parse_relational(self) -> int:
        value = self._parse_shift()
        while self._peek() in ("<", ">", "<=", ">="):
            op = self._take()
            rhs = self._parse_shift()
            if op == "<":
                value = int(value < rhs)
            elif op == ">":
                value = int(value > rhs)
            elif op == "<=":
                value = int(value <= rhs)
            else:
                value = int(value >= rhs)
        return value

    def _parse_shift(self) -> int:
        value = self._parse_additive()
        while self._peek() in ("<<", ">>"):
            op = self._take()
            rhs = self._parse_additive()
            value = value << rhs if op == "<<" else value >> rhs
        return value

    def _parse_additive(self) -> int:
        value = self._parse_multiplicative()
        while self._peek() in ("+", "-"):
            op = self._take()
            rhs = self._parse_multiplicative()
            value = value + rhs if op == "+" else value - rhs
        return value

    def _parse_multiplicative(self) -> int:
        value = self._parse_unary()
        while self._peek() in ("*", "/", "%"):
            op = self._take()
            rhs = self._parse_unary()
            if op == "*":
                value *= rhs
            elif op == "/":
                value = int(value / rhs) if rhs else 0
            else:
                value = value % rhs if rhs else 0
        return value

    def _parse_unary(self) -> int:
        token = self._peek()
        if token in ("!", "-", "+", "~"):
            op = self._take()
            value = self._parse_unary()
            if op == "!":
                return int(not value)
            if op == "-":
                return -value
            if op == "+":
                return value
            return ~value

        if token == "(":
            self._take()
            value = self._parse_or()
            if self._peek() == ")":
                self._take()
            return value

        return self._parse_primary()

    def _parse_primary(self) -> int:
        kind = self.tokens[self.index][0] if self.index < len(self.tokens) else None
        token = self._take()
        if token is None:
            return 0

        if kind == "number":
            try:
                return int(token, 0)
            except ValueError:
                return 0

        if kind == "ident":
            return self._macro_number(token)

        return 0


class PawnSourceTools:
    @staticmethod
    def split_lines(text: str) -> List[str]:
        return text.splitlines()

    @staticmethod
    def fingerprint(path: str) -> str:
        digest = hashlib.sha1()
        with open(path, "rb") as source:
            while True:
                chunk = source.read(1024 * 128)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def read_text(path: str) -> str:
        with open(path, "rb") as source:
            data = source.read()
        text, _encoding = PlatformUtils.decode_text(data)
        return text

    @staticmethod
    def normalized(path: str) -> str:
        return os.path.normcase(os.path.abspath(path))

    @staticmethod
    def public_path(path: str) -> str:
        return PlatformUtils.normalize_path(os.path.abspath(path))

    @staticmethod
    def strip_comments_and_strings(text: str, preserve_strings: bool = False) -> str:
        # Replace comments and, optionally, string/character literals with spaces
        # while preserving line breaks and character offsets.
        out = list(text)
        state = "code"
        escaped = False
        i = 0
        while i < len(text):
            c = text[i]
            nxt = text[i + 1] if i + 1 < len(text) else ""

            if state == "code":
                if c == "/" and nxt == "/":
                    out[i] = " "
                    out[i + 1] = " "
                    i += 2
                    state = "line_comment"
                    continue
                if c == "/" and nxt == "*":
                    out[i] = " "
                    out[i + 1] = " "
                    i += 2
                    state = "block_comment"
                    continue
                if c == '"':
                    if not preserve_strings:
                        out[i] = " "
                    state = "string"
                    escaped = False
                    i += 1
                    continue
                if c == "'":
                    if not preserve_strings:
                        out[i] = " "
                    state = "char"
                    escaped = False
                    i += 1
                    continue
                i += 1
                continue

            if state == "line_comment":
                if c == "\n":
                    state = "code"
                else:
                    out[i] = " "
                i += 1
                continue

            if state == "block_comment":
                if c == "*" and nxt == "/":
                    out[i] = " "
                    out[i + 1] = " "
                    i += 2
                    state = "code"
                else:
                    if c != "\n":
                        out[i] = " "
                    i += 1
                continue

            if state in ("string", "char"):
                if c == "\n":
                    state = "code"
                    escaped = False
                    continue
                if escaped:
                    if not preserve_strings:
                        out[i] = " "
                    escaped = False
                elif c == "\\":
                    if not preserve_strings:
                        out[i] = " "
                    escaped = True
                elif (state == "string" and c == '"') or (state == "char" and c == "'"):
                    if not preserve_strings:
                        out[i] = " "
                    state = "code"
                elif not preserve_strings:
                    out[i] = " "
                i += 1

        return "".join(out)

    @staticmethod
    def line_indent_column(line: str, offset: int = 0) -> int:
        return len(line) - len(line.lstrip()) + offset


class PawnProjectIndexer:
    """
    Pawn-aware project index.

    A .pwn file is a translation unit root. Includes are resolved exactly like
    a Pawn project include path, then preprocessed recursively. The resulting
    TU symbol set is cached in SQLite.
    """

    def __init__(self, project_path: str, on_updated=None, on_status=None):
        self.project_path = PawnSourceTools.normalized(project_path)
        self.on_updated = on_updated
        self.on_status = on_status

        self.cache_dir = os.path.join(self.project_path, ".spawn")
        self.db_path = os.path.join(self.cache_dir, "index.sqlite3")

        self.enabled = bool(self.project_path and os.path.isdir(self.project_path))
        self.ready = False

        self._lock = threading.RLock()
        self._worker_lock = threading.Lock()
        self._worker: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._refresh_pending = False

        self._file_paths: Dict[str, str] = {}
        self._rel_paths: Dict[str, str] = {}
        self._include_paths: List[str] = []
        self._completion_include_paths: List[str] = []
        self._build_defines: Dict[str, str] = {}
        self._roots: List[str] = []
        self._pragma_once: Set[str] = set()

    # -------------------- lifecycle --------------------

    def start(self) -> None:
        self.refresh_async()

    def stop(self) -> None:
        self._stop_event.set()
        worker = self._worker
        if worker and worker.is_alive():
            worker.join(timeout=0.5)
        self._worker = None
        self.ready = False
        self._stop_event.clear()

    def _set_status(self, text):
        if self.on_status:
            try:
                self.on_status(text)
            except Exception as exc:
                SpawnLogger.error(f"Pawn indexer status callback: {exc}")

    def refresh_async(self, changed_paths: Optional[Sequence[str]] = None) -> None:
        if not self.enabled:
            return

        with self._worker_lock:
            if self._worker and self._worker.is_alive():
                self._refresh_pending = True
                return

            self._refresh_pending = False
            self._set_status("Updating project index...")
            self._worker = threading.Thread(
                target=self._refresh_worker,
                args=(list(changed_paths or []),),
                name="PawnProjectIndexer",
                daemon=True,
            )
            self._worker.start()

    def refresh(self, changed_paths: Optional[Sequence[str]] = None) -> bool:
        if not self.enabled:
            return False
        try:
            self._rebuild(list(changed_paths or []))
            return True
        except Exception as exc:
            SpawnLogger.error(f"Pawn indexer: {exc}")
            return False

    def _refresh_worker(self, changed_paths: List[str]) -> None:
        try:
            self._rebuild(changed_paths)
        except Exception as exc:
            SpawnLogger.error(f"Pawn indexer: {exc}")
        finally:
            with self._worker_lock:
                repeat = self._refresh_pending
                self._refresh_pending = False
                self._worker = None
            if repeat and not self._stop_event.is_set():
                self.refresh_async()

    # -------------------- project discovery --------------------

    def _discover_files(self) -> List[str]:
        ignored = {
            ".git", ".spawn", ".vscode", ".idea", "__pycache__",
            "node_modules", "logs", ".cache"
        }

        found: List[str] = []
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [
                d for d in dirs
                if d not in ignored
                and not d.startswith(".git")
            ]
            for name in files:
                if name.lower().endswith((".pwn", ".inc")):
                    found.append(PawnSourceTools.normalized(os.path.join(root, name)))
        return sorted(found)

    def _load_project_configuration(self) -> None:
        include_dirs: List[str] = []
        defines: Dict[str, str] = {}

        pawn_json = os.path.join(self.project_path, "pawn.json")
        data = {}
        if os.path.isfile(pawn_json):
            try:
                with open(pawn_json, "r", encoding="utf-8") as source:
                    data = json.load(source)
            except Exception:
                data = {}

        builds = data.get("builds") if isinstance(data, dict) else None
        if isinstance(builds, list):
            for build in builds:
                if not isinstance(build, dict):
                    continue
                for item in build.get("includes", []):
                    if isinstance(item, str):
                        include_dirs.append(item)
                for arg in build.get("args", []):
                    self._parse_compiler_define(arg, defines)

        for arg in data.get("args", []) if isinstance(data, dict) else []:
            self._parse_compiler_define(arg, defines)

        # Paths used by the resolver are intentionally broad so that legacy
        # projects can still resolve includes. Completion uses a narrower list
        # and does not expose arbitrary project source directories as libraries.
        resolver_builtin_dirs = [
            os.path.join(self.project_path, "pawno", "include"),
            os.path.join(self.project_path, "qawno", "include"),
            os.path.join(self.project_path, "include"),
            os.path.join(self.project_path, "legacy"),
            os.path.join(self.project_path, "dependencies"),
            os.path.join(self.project_path, "gamemodes"),
            self.project_path,
        ]
        completion_builtin_dirs = [
            os.path.join(self.project_path, "pawno", "include"),
            os.path.join(self.project_path, "qawno", "include"),
            os.path.join(self.project_path, "include"),
            os.path.join(self.project_path, "legacy"),
            os.path.join(self.project_path, "dependencies"),
        ]

        def resolve_dirs(items):
            result = []
            seen = set()
            for item in items:
                absolute = item
                if not os.path.isabs(absolute):
                    absolute = os.path.join(self.project_path, item)
                absolute = PawnSourceTools.normalized(absolute)
                if absolute in seen:
                    continue
                seen.add(absolute)
                if os.path.isdir(absolute):
                    result.append(absolute)
            return result

        self._include_paths = resolve_dirs(include_dirs + resolver_builtin_dirs)
        self._completion_include_paths = resolve_dirs(include_dirs + completion_builtin_dirs)
        self._build_defines = defines

    @staticmethod
    def _parse_compiler_define(arg, defines: Dict[str, str]) -> None:
        if not isinstance(arg, str):
            return
        token = arg.strip()
        if not token:
            return
        match = re.match(r"^(?:-D|/D)([A-Za-z_][A-Za-z0-9_]*)(?:=(.*))?$", token)
        if not match:
            return
        defines[match.group(1)] = match.group(2) if match.group(2) is not None else "1"

    def _prepare_lookup(self, files: Sequence[str]) -> None:
        self._file_paths.clear()
        self._rel_paths.clear()

        root = self.project_path
        for path in files:
            rel = os.path.relpath(path, root).replace("\\", "/")
            self._file_paths[PawnSourceTools.normalized(path)] = PawnSourceTools.public_path(path)
            self._rel_paths[PawnSourceTools.normalized(rel)] = path

    # -------------------- include resolution --------------------

    def _resolve_include(self, source_path: str, include_name: str, quoted: bool) -> Optional[str]:
        normalized_name = include_name.strip().replace("\\", "/")
        if not normalized_name:
            return None

        candidates = []
        if not normalized_name.lower().endswith(".inc"):
            candidates.append(normalized_name + ".inc")
        candidates.append(normalized_name)

        source_dir = os.path.dirname(source_path)

        search_dirs: List[str] = []
        if quoted:
            search_dirs.append(source_dir)
        search_dirs.extend(self._include_paths)

        seen = set()
        for directory in search_dirs:
            directory = PawnSourceTools.normalized(directory)
            for candidate in candidates:
                full = PawnSourceTools.normalized(os.path.join(directory, candidate))
                if full in seen:
                    continue
                seen.add(full)
                if full in self._file_paths:
                    return full

        # Exact project-relative lookup is useful for odd custom layouts.
        for candidate in candidates:
            full = PawnSourceTools.normalized(os.path.join(self.project_path, candidate))
            if full in self._file_paths:
                return full

        # Last resort: match a unique project file by include spelling.
        # Pawn dependencies are often nested deeply, e.g.
        # dependencies/pawn-lang/samp-stdlib/.../a_samp.inc, while the source
        # simply says #include <a_samp>.  The normal include directories may not
        # point at that package root, so a unique basename fallback is useful.
        suffix = normalized_name.lstrip("./").casefold()
        if not suffix.endswith(".inc"):
            suffix_with_ext = suffix + ".inc"
        else:
            suffix_with_ext = suffix

        matches = []
        for path in self._file_paths:
            rel = os.path.relpath(path, self.project_path).replace("\\", "/").casefold()
            basename = os.path.basename(rel)
            if (
                rel == suffix
                or rel == suffix_with_ext
                or rel.endswith("/" + suffix)
                or rel.endswith("/" + suffix_with_ext)
                or basename == suffix
                or basename == suffix_with_ext
            ):
                matches.append(path)

        if len(matches) == 1:
            return matches[0]
        return None

    # -------------------- parsing --------------------

    def _parse_file(self, path: str) -> ParsedFile:
        path = PawnSourceTools.normalized(path)
        text = PawnSourceTools.read_text(path)
        fingerprint = PawnSourceTools.fingerprint(path)

        code = PawnSourceTools.strip_comments_and_strings(text, preserve_strings=False)
        directives = PawnSourceTools.strip_comments_and_strings(text, preserve_strings=True)
        code_lines = code.splitlines()
        directive_lines = directives.splitlines()

        includes: List[PawnInclude] = []
        pragma_once = False

        for index, line in enumerate(directive_lines, start=1):
            include_match = _INCLUDE_RE.match(line)
            if include_match:
                directive, delimiter, include_name = include_match.groups()
                target = self._resolve_include(
                    path,
                    include_name,
                    quoted=(delimiter == '"'),
                )
                includes.append(
                    PawnInclude(
                        source_path=path,
                        line=index,
                        include_name=include_name,
                        target_path=target,
                        required=(directive.lower() == "include"),
                    )
                )
                continue

            if _PRAGMA_ONCE_RE.match(line):
                pragma_once = True

        symbols = self._parse_symbols(path, code_lines, directive_lines)
        return ParsedFile(
            path=path,
            fingerprint=fingerprint,
            symbols=symbols,
            includes=includes,
            pragma_once=pragma_once,
        )

    def _parse_symbols(
        self,
        path: str,
        code_lines: Sequence[str],
        directive_lines: Sequence[str],
    ) -> List[PawnSymbol]:
        symbols: List[PawnSymbol] = []

        functions: List[PawnSymbol] = []
        function_ranges: List[Tuple[int, int]] = []

        line_count = len(code_lines)

        # Function declarations/definitions and commands.
        line = 0
        while line < line_count:
            raw = code_lines[line]

            cmd_match = _COMMAND_RE.match(raw)
            if cmd_match:
                command_name = f"{cmd_match.group(1).upper()}:{cmd_match.group(2)}"
                signature = self._collect_signature(code_lines, line)
                end_line = self._find_function_end(code_lines, line, line_count)
                symbol = PawnSymbol(
                    name=command_name,
                    kind="command",
                    line=line + 1,
                    column=max(0, raw.find(command_name)),
                    scope_start=line + 1,
                    scope_end=end_line,
                    signature=signature,
                    detail="command callback",
                )
                functions.append(symbol)
                function_ranges.append((line + 1, end_line))
                line += 1
                continue

            candidate = _FUNCTION_PREFIX_RE.match(raw)
            if not candidate:
                line += 1
                continue

            prefix, tag, name = candidate.groups()
            if name.lower() in _CONTROL_NAMES:
                line += 1
                continue

            prefix = prefix.lower() if prefix else ""
            signature = self._collect_signature(code_lines, line)
            has_body, has_prototype = self._classify_function_declaration(
                code_lines, line
            )
            if prefix in ("native", "forward"):

                if not (has_prototype or has_body):
                    line += 1
                    continue
            elif not has_body:
                line += 1
                continue

            kind = prefix or "function"
            detail = kind
            if tag:
                detail = f"{kind} {tag}:"

            end_line = (
                self._find_function_end(code_lines, line, line_count)
                if has_body
                else line + 1
            )

            functions.append(
                PawnSymbol(
                    name=name,
                    kind=kind,
                    line=line + 1,
                    column=max(0, raw.find(name)),
                    scope_start=line + 1,
                    scope_end=end_line if has_body else 0,
                    signature=signature,
                    detail=detail,
                )
            )

            if has_body:
                function_ranges.append((line + 1, end_line))

            line += 1

        symbols.extend(functions)

        # Function parameters.
        for function in functions:
            if function.kind in ("native", "forward"):
                continue
            params = self._extract_parameters(function.signature)
            for parameter in params:
                symbols.append(
                    PawnSymbol(
                        name=parameter,
                        kind="parameter",
                        line=function.line,
                        column=0,
                        scope_start=function.scope_start,
                        scope_end=function.scope_end,
                        signature="",
                        detail=f"parameter of {function.name}",
                        local=True,
                    )
                )

        # #define / typedef / enum.
        enum_depth = 0
        enum_name = None
        enum_start = 0
        for index, raw_directive in enumerate(directive_lines, start=1):
            define_match = _DEFINE_SYMBOL_RE.match(raw_directive)
            if define_match:
                name = define_match.group(1)
                symbols.append(
                    PawnSymbol(
                        name=name,
                        kind="macro",
                        line=index,
                        column=max(0, raw_directive.find(name)),
                        signature=self._get_define_signature(raw_directive),
                        detail="preprocessor macro",
                    )
                )

            typedef_match = _TYPEDEF_RE.match(raw_directive)
            if typedef_match:
                name = typedef_match.group(1)
                symbols.append(
                    PawnSymbol(
                        name=name,
                        kind="typedef",
                        line=index,
                        column=max(0, raw_directive.find(name)),
                        detail="typedef",
                    )
                )

        # Enum parser. Pawn commonly puts the opening brace on the next line,
        # so keep a pending state rather than treating the declaration line as
        # an already-open enum.
        enum_depth = 0
        enum_pending = False
        current_enum = None
        for index, raw in enumerate(code_lines, start=1):
            stripped = raw.strip()

            if enum_depth == 0 and not enum_pending:
                match = _ENUM_RE.match(raw)
                if not match:
                    continue

                current_enum = match.group(1)
                if current_enum:
                    symbols.append(
                        PawnSymbol(
                            name=current_enum,
                            kind="enum",
                            line=index,
                            column=max(0, raw.find(current_enum)),
                            detail="enum",
                        )
                    )

                open_pos = raw.find("{")
                if open_pos >= 0:
                    enum_depth = max(1, raw.count("{", open_pos) - raw.count("}", open_pos))
                    enum_pending = False
                else:
                    enum_pending = True
                continue

            if enum_pending:
                open_pos = stripped.find("{")
                if open_pos < 0:
                    continue
                enum_pending = False
                enum_depth = max(1, stripped.count("{", open_pos) - stripped.count("}", open_pos))
                remainder = stripped[open_pos + 1:]
                if remainder and enum_depth > 0:
                    parts = re.split(r",", remainder)
                    for part in parts:
                        part = part.strip().rstrip("}").strip()
                        match = re.match(r"(?:[A-Za-z_][A-Za-z0-9_]*\s*:\s*)?([A-Za-z_][A-Za-z0-9_]*)", part)
                        if match and match.group(1).lower() not in _PAWN_KEYWORDS:
                            name = match.group(1)
                            symbols.append(
                                PawnSymbol(
                                    name=name,
                                    kind="enum_value",
                                    line=index,
                                    column=max(0, raw.find(name)),
                                    scope_start=0,
                                    scope_end=0,
                                    detail=f"enum {current_enum or ''}".strip(),
                                )
                            )
                if enum_depth <= 0:
                    enum_depth = 0
                    current_enum = None
                continue

            # Inside enum body: only the first identifier of each enumerator
            # is a value. Do not treat arbitrary code-like lines as enum values.
            body = stripped
            brace_delta = body.count("{") - body.count("}")
            value_text = body.split("}", 1)[0] if "}" in body else body
            for part in re.split(r",", value_text):
                part = part.strip()
                if not part:
                    continue
                match = re.match(
                    r"(?:[A-Za-z_][A-Za-z0-9_]*\s*:\s*)?([A-Za-z_][A-Za-z0-9_]*)",
                    part,
                )
                if match and match.group(1).lower() not in _PAWN_KEYWORDS:
                    name = match.group(1)
                    symbols.append(
                        PawnSymbol(
                            name=name,
                            kind="enum_value",
                            line=index,
                            column=max(0, raw.find(name)),
                            scope_start=0,
                            scope_end=0,
                            detail=f"enum {current_enum or ''}".strip(),
                        )
                    )

            enum_depth += brace_delta
            if enum_depth <= 0:
                enum_depth = 0
                current_enum = None

        # Variables/constants. Build lexical block scopes so local symbols are
        # only visible inside the block in which they are declared. Pawn allows
        # both one-line and multiline declarations ("new\n    a,\n    b;").
        block_ranges = self._build_block_ranges(code_lines, function_ranges)
        index = 0
        while index < line_count:
            raw = code_lines[index]
            match = _DECL_RE.match(raw)
            if not match:
                index += 1
                continue

            keyword = match.group(1).lower()
            first_rest = match.group(2).strip()
            rest_parts = [first_rest] if first_rest else []
            end_index = index

            # Continue a declaration until its terminating semicolon. This is
            # required for the common Pawn style where `new` is on its own line.
            combined = first_rest
            if ";" not in PawnSourceTools.strip_comments_and_strings(combined):
                scan = index + 1
                while scan < line_count:
                    part = code_lines[scan].strip()
                    rest_parts.append(part)
                    combined = " ".join(rest_parts)
                    end_index = scan
                    if ";" in PawnSourceTools.strip_comments_and_strings(combined):
                        break
                    scan += 1

            rest = " ".join(rest_parts).strip().rstrip(";")
            if not rest or rest.startswith("("):
                index = end_index + 1
                continue

            declaration_parts = self._split_declarations(rest)
            enclosing = self._find_enclosing_function(index + 1, function_ranges)
            enclosing_block = (
                self._find_innermost_block(index + 1, block_ranges, enclosing)
                if enclosing else None
            )

            for part in declaration_parts:
                part = part.strip().rstrip(";")
                if not part:
                    continue

                # Ignore initializers when extracting the declared identifier.
                declaration = part.split("=", 1)[0].strip()
                name = self._extract_declared_name(declaration)
                if not name or name in _PAWN_KEYWORDS:
                    continue

                kind = "constant" if keyword == "const" else "variable"
                if keyword == "static":
                    kind = "static"

                local = enclosing is not None
                if local:
                    scope_start, scope_end = enclosing_block or enclosing
                else:
                    scope_start, scope_end = 0, 0

                symbols.append(
                    PawnSymbol(
                        name=name,
                        kind=kind,
                        line=index + 1,
                        column=max(0, raw.find(name)),
                        scope_start=scope_start,
                        scope_end=scope_end,
                        detail=keyword,
                        local=local,
                    )
                )

            index = end_index + 1

        # Pawn also permits declarations inside control statements, most
        # notably `for (new i = 0; ...)`. Capture those declarations as local
        # symbols as well. The line is sanitized first so `new` inside a
        # string/comment cannot become a false symbol.
        for index, raw in enumerate(code_lines, start=1):
            enclosing = self._find_enclosing_function(index, function_ranges)
            if enclosing is None:
                continue

            sanitized = PawnSourceTools.strip_comments_and_strings(raw)
            inline_matches = re.finditer(
                r"\b(new|static|const|decl)\s+([^;)]*)",
                sanitized,
                re.IGNORECASE,
            )
            for decl_match in inline_matches:
                keyword = decl_match.group(1).lower()
                rest = decl_match.group(2).strip()
                if not rest:
                    continue
                # The normal declaration pass already handles declarations at
                # the beginning of a line; duplicates are removed below.
                for part in self._split_declarations(rest):
                    declaration = part.split("=", 1)[0].strip()
                    name = self._extract_declared_name(declaration)
                    if not name or name in _PAWN_KEYWORDS:
                        continue
                    block = self._find_innermost_block(index, block_ranges, enclosing)
                    scope_start, scope_end = block or enclosing
                    loop_scope = self._find_loop_scope(code_lines, index)
                    if loop_scope is not None:
                        scope_start, scope_end = loop_scope
                    kind = "constant" if keyword == "const" else (
                        "static" if keyword == "static" else "variable"
                    )
                    symbols.append(
                        PawnSymbol(
                            name=name,
                            kind=kind,
                            line=index,
                            column=max(0, raw.find(name)),
                            scope_start=scope_start,
                            scope_end=scope_end,
                            detail=keyword,
                            local=True,
                        )
                    )

        # Deduplicate exact source declarations, preserving order.
        unique = {}
        result = []
        for symbol in symbols:
            key = (
                symbol.name.casefold(),
                symbol.kind,
                symbol.line,
                symbol.column,
            )
            if key in unique:
                continue
            unique[key] = True
            result.append(symbol)
        return result

    @staticmethod
    def _classify_function_declaration(
        lines: Sequence[str],
        start: int,
    ) -> Tuple[bool, bool]:
        """Classify a function-like line as a definition or prototype.

        Pawn has many ordinary function calls that look exactly like a
        function declaration at the start of a line. A definition is only
        accepted when the first meaningful token after the closing ')' is '{'
        (on the same or following line), while a prototype must terminate in ';'.
        """
        depth = 0
        seen_open = False
        close_line = -1
        close_column = -1

        for index in range(start, min(len(lines), start + 32)):
            cleaned = re.sub(
                r'//.*$|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                lambda m: " " * len(m.group(0)),
                lines[index],
            )
            for column, char in enumerate(cleaned):
                if char == "(":
                    depth += 1
                    seen_open = True
                elif char == ")" and seen_open:
                    depth -= 1
                    if depth == 0:
                        close_line = index
                        close_column = column
                        break
            if close_line >= 0:
                break

        if close_line < 0:
            return False, False

        remainder = re.sub(
            r'//.*$|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
            lambda m: " " * len(m.group(0)),
            lines[close_line][close_column + 1:],
        ).strip()
        if remainder:
            if remainder.startswith("{"):
                return True, False
            if remainder.startswith(";"):
                return False, True
            # A brace later on the same line is valid only if no statement
            # terminator comes first.
            brace = remainder.find("{")
            semi = remainder.find(";")
            if brace >= 0 and (semi < 0 or brace < semi):
                return True, False
            if semi >= 0:
                return False, True
            return False, False

        # Brace/prototype may be on the next physical line. Skip comments and
        # blank lines, but do not scan arbitrarily far into the next statement.
        for index in range(close_line + 1, min(len(lines), close_line + 8)):
            cleaned = re.sub(
                r'//.*$|/\*.*?\*/',
                "",
                lines[index],
            ).strip()
            if not cleaned:
                continue
            if cleaned.startswith("{"):
                return True, False
            if cleaned.startswith(";"):
                return False, True
            return False, False

        return False, False

    @staticmethod
    def _collect_signature(lines: Sequence[str], start: int) -> str:
        pieces = []
        depth = 0
        for index in range(start, min(len(lines), start + 12)):
            line = lines[index].strip()
            pieces.append(line)
            depth += line.count("(") - line.count(")")
            if depth <= 0 and ")" in line:
                break
        text = " ".join(pieces)
        text = re.sub(r"\s+", " ", text).strip()
        # Calltips should show the callable declaration, not its body.
        close = text.find(")")
        if close >= 0:
            text = text[: close + 1]
        return text.strip()

    @staticmethod
    def _find_function_end(lines: Sequence[str], start: int, line_count: int) -> int:
        depth = 0
        seen_open = False
        for index in range(start, line_count):
            line = lines[index]
            opens = line.count("{")
            closes = line.count("}")
            if opens:
                seen_open = True
            if seen_open:
                depth += opens - closes
                if depth <= 0:
                    return index + 1
        return line_count

    @staticmethod
    def _is_probable_function_definition(lines: Sequence[str], start: int) -> bool:
        block = " ".join(lines[start:min(len(lines), start + 4)])
        if ";" in block.split(")", 1)[-1] if ")" in block else False:
            return False
        return "{" in block

    @staticmethod
    def _extract_parameters(signature: str) -> List[str]:
        match = re.search(r"\((.*)\)", signature)
        if not match:
            return []
        body = match.group(1).strip()
        if not body:
            return []
        result = []
        parts = []
        current = []
        depth = 0
        for char in body:
            if char in "([{":
                depth += 1
            elif char in ")]}":
                depth = max(0, depth - 1)
            if char == "," and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)
        parts.append("".join(current))

        for part in parts:
            declaration = part.split("=", 1)[0].strip()
            name = PawnProjectIndexer._extract_declared_name(declaration)
            if not name or name.lower() in _PAWN_KEYWORDS:
                continue
            result.append(name)
        return result

    @staticmethod
    def _extract_declared_name(declaration: str) -> str:
        """Extract the declared Pawn identifier from one declarator.

        Supports common forms such as:
            foo
            foo[32]
            Float:foo
            const foo
            static PlayerText:foo[3]
        """
        value = declaration.strip()
        value = re.sub(r"\b(const|static)\b\s+", "", value, count=1, flags=re.IGNORECASE)
        match = re.match(
            r"^(?:[A-Za-z_][A-Za-z0-9_]*\s*:\s*)?([A-Za-z_][A-Za-z0-9_]*)",
            value,
        )
        return match.group(1) if match else ""

    @staticmethod
    def _build_block_ranges(
        lines: Sequence[str],
        function_ranges: Sequence[Tuple[int, int]],
    ) -> List[Tuple[int, int]]:
        """Return innermost lexical brace blocks inside Pawn functions."""
        ranges: List[Tuple[int, int]] = []
        stack: List[int] = []
        for index, raw in enumerate(lines, start=1):
            cleaned = re.sub(
                r'//.*$|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                lambda m: " " * len(m.group(0)),
                raw,
            )
            for char in cleaned:
                if char == "{":
                    stack.append(index)
                elif char == "}" and stack:
                    start = stack.pop()
                    ranges.append((start, index))
        return ranges

    @staticmethod
    def _find_innermost_block(
        line: int,
        block_ranges: Sequence[Tuple[int, int]],
        function_range: Optional[Tuple[int, int]],
    ) -> Optional[Tuple[int, int]]:
        candidates = [
            pair for pair in block_ranges
            if pair[0] <= line <= pair[1]
            and (function_range is None or function_range[0] <= pair[0] <= function_range[1])
        ]
        if not candidates:
            return function_range
        start, end = min(candidates, key=lambda pair: (pair[1] - pair[0], -pair[0]))
        # The closing brace itself is outside the lexical scope.
        return start, max(start, end - 1)

    @staticmethod
    def _split_declarations(rest: str) -> List[str]:
        parts = []
        current = []
        depth = 0
        in_string = False
        escaped = False
        for char in rest:
            if in_string:
                current.append(char)
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
                current.append(char)
                continue
            if char in "[(":
                depth += 1
            elif char in "])":
                depth = max(0, depth - 1)
            if char == "," and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)
        if current:
            parts.append("".join(current))
        return parts

    @staticmethod
    def _find_loop_scope(lines: Sequence[str], line: int) -> Optional[Tuple[int, int]]:
        """Return the lexical scope of a variable declared in for/foreach.

        Pawn permits declarations such as `for (new i = 0; ... )` and
        `foreach (new i : Players)`. Such a variable must not leak past the
        loop, even though the loop may live inside a larger brace block.
        """
        if line < 1 or line > len(lines):
            return None
        raw = PawnSourceTools.strip_comments_and_strings(lines[line - 1])
        if not re.search(r"\b(?:for|foreach)\s*\(", raw, re.IGNORECASE):
            return None

        # Locate the first body token after the control expression.
        paren = 0
        close_pos = -1
        open_pos = raw.find("(")
        if open_pos < 0:
            return None
        for pos in range(open_pos, len(raw)):
            char = raw[pos]
            if char == "(":
                paren += 1
            elif char == ")":
                paren -= 1
                if paren == 0:
                    close_pos = pos
                    break
        if close_pos < 0:
            return None

        remainder = raw[close_pos + 1:].strip()
        if remainder.startswith("{"):
            depth = 0
            for idx in range(line - 1, len(lines)):
                cleaned = PawnSourceTools.strip_comments_and_strings(lines[idx])
                for char in cleaned:
                    if char == "{":
                        depth += 1
                    elif char == "}" and depth:
                        depth -= 1
                        if depth == 0:
                            return line, max(line, idx)
            return line, len(lines)

        # Body begins on the next non-empty line.
        body_line = line + 1
        while body_line <= len(lines) and not lines[body_line - 1].strip():
            body_line += 1
        if body_line > len(lines):
            return line, line

        body = PawnSourceTools.strip_comments_and_strings(lines[body_line - 1]).strip()
        if body.startswith("{"):
            depth = 0
            for idx in range(body_line - 1, len(lines)):
                cleaned = PawnSourceTools.strip_comments_and_strings(lines[idx])
                for char in cleaned:
                    if char == "{":
                        depth += 1
                    elif char == "}" and depth:
                        depth -= 1
                        if depth == 0:
                            return line, max(line, idx)
            return line, len(lines)

        # Single-statement loop body.
        return line, body_line

    @staticmethod
    def _find_enclosing_function(line: int, ranges: Sequence[Tuple[int, int]]):
        candidates = [pair for pair in ranges if pair[0] <= line <= pair[1]]
        if not candidates:
            return None
        return min(candidates, key=lambda pair: pair[1] - pair[0])

    @staticmethod
    def _get_define_signature(line: str) -> str:
        match = _DEFINE_RE.match(line)
        if not match:
            return ""
        name = match.group(1)
        params = match.group(2)
        return f"#define {name}({params})" if params is not None else f"#define {name}"

    # -------------------- preprocessor / TU --------------------

    def _eval_condition(self, expr: str, macros: Dict[str, str]) -> bool:
        expr = re.sub(
            r"\bdefined\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)",
            lambda m: "1" if m.group(1) in macros else "0",
            expr,
            flags=re.IGNORECASE,
        )
        expr = re.sub(
            r"\bdefined\s+([A-Za-z_][A-Za-z0-9_]*)",
            lambda m: "1" if m.group(1) in macros else "0",
            expr,
            flags=re.IGNORECASE,
        )
        try:
            return bool(_ExpressionParser(expr, macros).parse())
        except Exception:
            return False

    def _initial_macros(self) -> Dict[str, str]:
        return dict(self._build_defines)

    def _build_translation_unit(
        self,
        root_path: str,
        parsed: Dict[str, ParsedFile],
    ) -> Tuple[Set[str], Dict[str, Set[int]]]:
        macros = self._initial_macros()
        visited_stack: List[str] = []
        processed_pragma_once: Set[str] = set()
        active_lines: Dict[str, Set[int]] = {}

        def process(path: str):
            path = PawnSourceTools.normalized(path)
            if path in visited_stack:
                return
            if path in processed_pragma_once:
                return

            file_info = parsed.get(path)
            if file_info is None:
                return

            visited_stack.append(path)
            if file_info.pragma_once:
                processed_pragma_once.add(path)

            try:
                directives = PawnSourceTools.strip_comments_and_strings(
                    PawnSourceTools.read_text(path), preserve_strings=True
                ).splitlines()

                active = True
                stack: List[Dict[str, object]] = []
                lines = active_lines.setdefault(path, set())

                for index, raw in enumerate(directives, start=1):
                    if _IF_RE.match(raw):
                        expr = _IF_RE.match(raw).group(1)
                        parent = active
                        condition = self._eval_condition(expr, macros)
                        stack.append(
                            {
                                "parent": parent,
                                "taken": condition,
                                "active": parent and condition,
                            }
                        )
                        active = bool(parent and condition)
                        continue

                    if _IFDEF_RE.match(raw):
                        name = _IFDEF_RE.match(raw).group(1)
                        parent = active
                        condition = name in macros
                        stack.append(
                            {
                                "parent": parent,
                                "taken": condition,
                                "active": parent and condition,
                            }
                        )
                        active = bool(parent and condition)
                        continue

                    if _IFNDEF_RE.match(raw):
                        name = _IFNDEF_RE.match(raw).group(1)
                        parent = active
                        condition = name not in macros
                        stack.append(
                            {
                                "parent": parent,
                                "taken": condition,
                                "active": parent and condition,
                            }
                        )
                        active = bool(parent and condition)
                        continue

                    if _ELSEIF_RE.match(raw):
                        if not stack:
                            continue
                        frame = stack[-1]
                        parent = bool(frame["parent"])
                        taken = bool(frame["taken"])
                        condition = self._eval_condition(_ELSEIF_RE.match(raw).group(1), macros)
                        frame["taken"] = taken or condition
                        active = bool(parent and (not taken) and condition)
                        continue

                    if _ELSE_RE.match(raw):
                        if not stack:
                            continue
                        frame = stack[-1]
                        parent = bool(frame["parent"])
                        taken = bool(frame["taken"])
                        active = bool(parent and not taken)
                        frame["taken"] = True
                        continue

                    if _ENDIF_RE.match(raw):
                        if not stack:
                            continue
                        frame = stack.pop()
                        active = bool(frame["parent"])
                        continue

                    if not active:
                        continue

                    lines.add(index)

                    define_match = _DEFINE_RE.match(raw)
                    if define_match:
                        name = define_match.group(1)
                        value = (define_match.group(3) or "").strip()
                        macros[name] = value or "1"
                        continue

                    undef_match = _UNDEF_RE.match(raw)
                    if undef_match:
                        macros.pop(undef_match.group(1), None)
                        continue

                    if _PRAGMA_ONCE_RE.match(raw):
                        processed_pragma_once.add(path)
                        continue

                    if _ENDINPUT_RE.match(raw):
                        break

                    include_match = _INCLUDE_RE.match(raw)
                    if include_match:
                        target = next(
                            (
                                include.target_path
                                for include in file_info.includes
                                if include.line == index
                            ),
                            None,
                        )
                        if target:
                            process(target)

            finally:
                visited_stack.pop()

        process(root_path)
        return set(active_lines.keys()), active_lines

    # -------------------- sqlite --------------------

    def _open_db(self) -> sqlite3.Connection:
        os.makedirs(self.cache_dir, exist_ok=True)
        connection = sqlite3.connect(
            self.db_path,
            timeout=10,
            check_same_thread=False,
        )
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA foreign_keys=ON")
        self._init_db(connection)
        # Migrate databases created by earlier development versions.
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(files)").fetchall()
        }
        if "indexed" not in columns:
            connection.execute(
                "ALTER TABLE files ADD COLUMN indexed INTEGER NOT NULL DEFAULT 0"
            )
            connection.commit()
        return connection

    @staticmethod
    def _init_db(db: sqlite3.Connection) -> None:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                relpath TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                pragma_once INTEGER NOT NULL DEFAULT 0,
                indexed INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY,
                file_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                line INTEGER NOT NULL,
                column_no INTEGER NOT NULL DEFAULT 0,
                scope_start INTEGER NOT NULL DEFAULT 0,
                scope_end INTEGER NOT NULL DEFAULT 0,
                signature TEXT NOT NULL DEFAULT '',
                detail TEXT NOT NULL DEFAULT '',
                local INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_symbols_file
                ON symbols(file_id);
            CREATE INDEX IF NOT EXISTS idx_symbols_name
                ON symbols(name);

            CREATE TABLE IF NOT EXISTS includes (
                id INTEGER PRIMARY KEY,
                file_id INTEGER NOT NULL,
                line INTEGER NOT NULL,
                include_name TEXT NOT NULL,
                target_file_id INTEGER,
                required INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE,
                FOREIGN KEY(target_file_id) REFERENCES files(id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_includes_file
                ON includes(file_id);
            CREATE INDEX IF NOT EXISTS idx_includes_target
                ON includes(target_file_id);

            CREATE TABLE IF NOT EXISTS translation_units (
                id INTEGER PRIMARY KEY,
                root_file_id INTEGER NOT NULL UNIQUE,
                FOREIGN KEY(root_file_id) REFERENCES files(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tu_files (
                tu_id INTEGER NOT NULL,
                file_id INTEGER NOT NULL,
                PRIMARY KEY(tu_id, file_id),
                FOREIGN KEY(tu_id) REFERENCES translation_units(id) ON DELETE CASCADE,
                FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tu_symbols (
                tu_id INTEGER NOT NULL,
                symbol_id INTEGER NOT NULL,
                PRIMARY KEY(tu_id, symbol_id),
                FOREIGN KEY(tu_id) REFERENCES translation_units(id) ON DELETE CASCADE,
                FOREIGN KEY(symbol_id) REFERENCES symbols(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_tu_symbols
                ON tu_symbols(tu_id, symbol_id);
            """
        )
        db.commit()

    def _load_cached_file(self, db: sqlite3.Connection, path: str) -> Optional[ParsedFile]:
        path = PawnSourceTools.normalized(path)
        row = db.execute(
            "SELECT id, fingerprint, pragma_once, indexed FROM files WHERE path=?",
            (path,),
        ).fetchone()
        if not row or not row[3]:
            return None

        try:
            fingerprint = PawnSourceTools.fingerprint(path)
        except OSError:
            return None

        if fingerprint != row[1]:
            return None

        file_id = row[0]

        symbol_rows = db.execute(
            """
            SELECT name, kind, line, column_no, scope_start, scope_end,
                   signature, detail, local
            FROM symbols
            WHERE file_id=?
            ORDER BY line, column_no
            """,
            (file_id,),
        ).fetchall()

        include_rows = db.execute(
            """
            SELECT line, include_name, required, target_file_id
            FROM includes
            WHERE file_id=?
            ORDER BY line
            """,
            (file_id,),
        ).fetchall()

        id_to_path = {
            value[0]: value[1]
            for value in db.execute("SELECT id, path FROM files")
        }

        symbols = [
            PawnSymbol(
                name=r[0], kind=r[1], line=r[2], column=r[3],
                scope_start=r[4], scope_end=r[5],
                signature=r[6], detail=r[7], local=bool(r[8]),
            )
            for r in symbol_rows
        ]

        includes = [
            PawnInclude(
                source_path=path,
                line=r[0],
                include_name=r[1],
                target_path=id_to_path.get(r[3]),
                required=bool(r[2]),
            )
            for r in include_rows
        ]
        return ParsedFile(
            path=path,
            fingerprint=fingerprint,
            symbols=symbols,
            includes=includes,
            pragma_once=bool(row[2]),
        )

    def _store_file(self, db: sqlite3.Connection, parsed: ParsedFile) -> None:
        relpath = os.path.relpath(parsed.path, self.project_path).replace("\\", "/")
        db.execute(
            """
            INSERT INTO files(path, relpath, fingerprint, pragma_once, indexed)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                relpath=excluded.relpath,
                fingerprint=excluded.fingerprint,
                pragma_once=excluded.pragma_once,
                indexed=excluded.indexed
            """,
            (parsed.path, relpath, parsed.fingerprint, int(parsed.pragma_once), 1),
        )
        file_id = db.execute(
            "SELECT id FROM files WHERE path=?",
            (parsed.path,),
        ).fetchone()[0]

        db.execute("DELETE FROM symbols WHERE file_id=?", (file_id,))
        db.execute("DELETE FROM includes WHERE file_id=?", (file_id,))

        for symbol in parsed.symbols:
            db.execute(
                """
                INSERT INTO symbols(
                    file_id, name, kind, line, column_no, scope_start,
                    scope_end, signature, detail, local
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file_id, symbol.name, symbol.kind, symbol.line, symbol.column,
                    symbol.scope_start, symbol.scope_end, symbol.signature,
                    symbol.detail, int(symbol.local),
                ),
            )

        for include in parsed.includes:
            target_id = None
            if include.target_path:
                target_row = db.execute(
                    "SELECT id FROM files WHERE path=?",
                    (include.target_path,),
                ).fetchone()
                if target_row:
                    target_id = target_row[0]

            db.execute(
                """
                INSERT INTO includes(
                    file_id, line, include_name, target_file_id, required
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    file_id, include.line, include.include_name,
                    target_id, int(include.required),
                ),
            )

    def _ensure_file_rows(self, db: sqlite3.Connection, files: Sequence[str]) -> None:
        keep = set(files)
        for path in files:
            relpath = os.path.relpath(path, self.project_path).replace("\\", "/")
            if not db.execute("SELECT 1 FROM files WHERE path=?", (path,)).fetchone():
                fingerprint = PawnSourceTools.fingerprint(path)
                db.execute(
                    """
                    INSERT INTO files(path, relpath, fingerprint, pragma_once, indexed)
                    VALUES (?, ?, ?, 0, 0)
                    """,
                    (path, relpath, fingerprint),
                )

        existing = [
            row[0]
            for row in db.execute("SELECT path FROM files").fetchall()
        ]
        for path in existing:
            if PawnSourceTools.normalized(path) not in keep:
                db.execute("DELETE FROM files WHERE path=?", (path,))

    # -------------------- rebuild --------------------

    def _rebuild(self, changed_paths: Sequence[str]) -> None:
        if self._stop_event.is_set():
            return

        files = self._discover_files()
        self._prepare_lookup(files)
        self._load_project_configuration()

        parsed: Dict[str, ParsedFile] = {}

        with self._open_db() as db:
            self._ensure_file_rows(db, files)

            for index, path in enumerate(files):
                if self._stop_event.is_set():
                    return
                cached = self._load_cached_file(db, path)
                if cached is not None:
                    parsed[path] = cached
                    continue

                try:
                    file_info = self._parse_file(path)
                except Exception as exc:
                    SpawnLogger.error(f"Pawn index parse '{path}': {exc}")
                    continue

                parsed[path] = file_info
                self._store_file(db, file_info)

            # Resolve include rows again now that every file row exists.
            for path, file_info in parsed.items():
                file_id_row = db.execute(
                    "SELECT id FROM files WHERE path=?", (path,)
                ).fetchone()
                if not file_id_row:
                    continue
                file_id = file_id_row[0]
                db.execute("DELETE FROM includes WHERE file_id=?", (file_id,))
                for include in file_info.includes:
                    target_id = None
                    if include.target_path:
                        row = db.execute(
                            "SELECT id FROM files WHERE path=?",
                            (include.target_path,),
                        ).fetchone()
                        if row:
                            target_id = row[0]
                    db.execute(
                        """
                        INSERT INTO includes(
                            file_id, line, include_name, target_file_id, required
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            file_id,
                            include.line,
                            include.include_name,
                            target_id,
                            int(include.required),
                        ),
                    )

            db.execute("DELETE FROM tu_files")
            db.execute("DELETE FROM tu_symbols")
            db.execute("DELETE FROM translation_units")

            root_paths = [
                path for path in files
                if path.lower().endswith(".pwn")
            ]
            self._roots = root_paths

            for root_path in root_paths:
                if self._stop_event.is_set():
                    return
                _reachable, active_map = self._build_translation_unit(root_path, parsed)

                root_id_row = db.execute(
                    "SELECT id FROM files WHERE path=?", (root_path,)
                ).fetchone()
                if not root_id_row:
                    continue
                root_id = root_id_row[0]

                cursor = db.execute(
                    "INSERT INTO translation_units(root_file_id) VALUES (?)",
                    (root_id,),
                )
                tu_id = cursor.lastrowid

                for member_path in sorted(active_map):
                    member_id_row = db.execute(
                        "SELECT id FROM files WHERE path=?", (member_path,)
                    ).fetchone()
                    if not member_id_row:
                        continue
                    member_id = member_id_row[0]
                    db.execute(
                        "INSERT OR IGNORE INTO tu_files(tu_id, file_id) VALUES (?, ?)",
                        (tu_id, member_id),
                    )

                    active_lines = active_map[member_path]
                    symbol_rows = db.execute(
                        """
                        SELECT id, line FROM symbols
                        WHERE file_id=?
                        """,
                        (member_id,),
                    ).fetchall()

                    for symbol_id, symbol_line in symbol_rows:
                        if symbol_line in active_lines:
                            db.execute(
                                "INSERT OR IGNORE INTO tu_symbols(tu_id, symbol_id) VALUES (?, ?)",
                                (tu_id, symbol_id),
                            )

            db.commit()

        with self._lock:
            self.ready = bool(self._roots)

        try:
            stats = self.statistics()
            SpawnLogger.info(
                "Pawn project index: files=%d, roots=%d, symbols=%d"
                % (stats["files"], stats["roots"], stats["symbols"])
            )
        except Exception:
            pass

        if self.on_updated:
            try:
                self.on_updated()
            except Exception as exc:
                SpawnLogger.error(f"Pawn indexer callback: {exc}")

    # -------------------- querying --------------------

    def statistics(self) -> Dict[str, int]:
        if not os.path.isfile(self.db_path):
            return {"files": 0, "roots": 0, "symbols": 0}

        with self._open_db() as db:
            files = db.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            roots = db.execute("SELECT COUNT(*) FROM translation_units").fetchone()[0]
            symbols = db.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
        return {
            "files": int(files),
            "roots": int(roots),
            "symbols": int(symbols),
        }

    def _find_root_ids_for_file(self, db: sqlite3.Connection, file_path: str) -> List[int]:
        file_path = PawnSourceTools.normalized(file_path)
        row = db.execute(
            "SELECT id FROM files WHERE path=?", (file_path,)
        ).fetchone()
        if not row:
            return []

        file_id = row[0]
        rows = db.execute(
            """
            SELECT tu.root_file_id
            FROM translation_units tu
            JOIN tu_files tf ON tf.tu_id = tu.id
            WHERE tf.file_id=?
            """,
            (file_id,),
        ).fetchall()
        return [int(r[0]) for r in rows]

    def _root_for_file(self, db: sqlite3.Connection, file_path: str) -> Optional[int]:
        file_path = PawnSourceTools.normalized(file_path)
        if file_path.lower().endswith(".pwn"):
            row = db.execute(
                """
                SELECT root_file_id FROM translation_units
                WHERE root_file_id = (SELECT id FROM files WHERE path=?)
                """,
                (file_path,),
            ).fetchone()
            if row:
                return int(row[0])

        roots = self._find_root_ids_for_file(db, file_path)
        return roots[0] if roots else None

    def query_include_completion(
        self,
        file_path: str,
        prefix: str = "",
        quoted: bool = False,
    ) -> List[Dict[str, object]]:
        """Return clean hierarchical completion for #include paths.

        At the root level only directly includable files and namespace folders
        are shown. A nested path is expanded only after the user has typed the
        separator, so a dependency with hundreds of .inc files does not flood
        the popup.
        """
        if not self.enabled or not self.ready:
            return []

        file_path = PawnSourceTools.normalized(file_path)
        if not file_path.lower().endswith((".pwn", ".inc")):
            return []

        normalized_prefix = (prefix or "").strip().replace("\\", "/")
        prefix_cf = normalized_prefix.casefold()
        has_namespace_prefix = "/" in normalized_prefix
        source_dir = os.path.dirname(file_path)

        with self._lock:
            candidates: Dict[str, Dict[str, object]] = {}
            search_dirs: List[str] = []
            if quoted:
                search_dirs.append(source_dir)
            search_dirs.extend(self._completion_include_paths)

            seen_dirs: Set[str] = set()
            for directory in search_dirs:
                directory = PawnSourceTools.normalized(directory)
                if directory in seen_dirs or not os.path.isdir(directory):
                    continue
                seen_dirs.add(directory)

                for target_path in self._file_paths:
                    if not target_path.lower().endswith(".inc"):
                        continue
                    try:
                        relative = os.path.relpath(target_path, directory).replace("\\", "/")
                    except ValueError:
                        continue
                    if relative == ".." or relative.startswith("../"):
                        continue

                    display = relative[:-4] if relative.lower().endswith(".inc") else relative
                    display = display.strip("/")
                    if not display:
                        continue

                    if prefix_cf:
                        if not display.casefold().startswith(prefix_cf):
                            continue
                        if has_namespace_prefix:
                            remainder = display[len(normalized_prefix):]
                            if remainder.startswith("/"):
                                remainder = remainder[1:]
                            if not remainder:
                                continue
                            slash = remainder.find("/")
                            if slash >= 0:
                                entry = normalized_prefix.rstrip("/") + "/" + remainder[:slash]
                                is_dir = True
                            else:
                                entry = normalized_prefix.rstrip("/") + "/" + remainder
                                is_dir = False
                        else:
                            # Text prefix without a namespace: a nested file is
                            # represented by its first folder, while direct files
                            # keep their complete include spelling.
                            slash = display.find("/")
                            if slash >= 0:
                                entry = display[:slash]
                                is_dir = True
                            else:
                                entry = display
                                is_dir = False
                    else:
                        slash = display.find("/")
                        if slash >= 0:
                            entry = display[:slash]
                            is_dir = True
                        else:
                            entry = display
                            is_dir = False

                    # A nested namespace is only a navigation entry until the
                    # user types its separator. It is not itself an includable
                    # file.
                    if is_dir and prefix_cf and has_namespace_prefix:
                        pass

                    key = (entry + "/" if is_dir else entry).casefold()
                    detail = PawnSourceTools.public_path(target_path)
                    candidate = {
                        "name": entry + ("/" if is_dir else ""),
                        "insert": entry + ("/" if is_dir else ""),
                        "kind": "include_folder" if is_dir else "include",
                        "detail": detail,
                        "file": target_path if not is_dir else None,
                        "is_dir": is_dir,
                        "_path_len": len(display),
                    }
                    current = candidates.get(key)
                    if current is None or int(candidate["_path_len"]) < int(current["_path_len"]):
                        candidates[key] = candidate

            result = list(candidates.values())
            for item in result:
                item.pop("_path_len", None)

            result.sort(
                key=lambda item: (
                    0 if bool(item.get("is_dir")) else 1,
                    str(item["name"]).casefold(),
                )
            )
            return result

    def query_callable(
        self,
        file_path: str,
        name: str,
        line: Optional[int] = None,
    ) -> List[Dict[str, object]]:
        """Return visible callable symbols matching an exact Pawn identifier."""
        if not name:
            return []
        callables = {"function", "native", "stock", "public", "forward", "hook", "command"}
        return [
            item
            for item in self.query_completion(file_path, prefix=name, line=line)
            if str(item.get("name", "")).casefold() == name.casefold()
            and str(item.get("kind", "")).casefold() in callables
            and str(item.get("signature", "")).strip()
        ]

    def query_completion(
        self,
        file_path: str,
        prefix: str = "",
        line: Optional[int] = None,
    ) -> List[Dict[str, object]]:
        if not self.enabled or not self.ready:
            return []

        file_path = PawnSourceTools.normalized(file_path)
        if not file_path.lower().endswith((".pwn", ".inc")):
            return []

        with self._lock:
            with self._open_db() as db:
                roots = []
                if file_path.lower().endswith(".pwn"):
                    root_id = self._root_for_file(db, file_path)
                    if root_id is not None:
                        roots = [root_id]
                else:
                    roots = self._find_root_ids_for_file(db, file_path)

                if not roots:
                    return []

                params = []
                placeholders = ",".join("?" for _ in roots)
                params.extend(roots)
                rows = db.execute(
                    f"""
                    SELECT DISTINCT s.name, s.kind, s.line, s.column_no,
                           s.scope_start, s.scope_end, s.signature, s.detail,
                           s.local, f.path
                    FROM tu_symbols ts
                    JOIN symbols s ON s.id = ts.symbol_id
                    JOIN translation_units tu ON tu.id = ts.tu_id
                    JOIN files f ON f.id = s.file_id
                    WHERE tu.root_file_id IN ({placeholders})
                    ORDER BY s.name COLLATE NOCASE
                    """,
                    params,
                ).fetchall()

                current_function = None
                if line is not None:
                    current_function = self._current_function_rows(
                        db, file_path, int(line)
                    )

                prefix_cf = prefix.casefold()
                result_by_name: Dict[str, Dict[str, object]] = {}

                for row in rows:
                    (
                        name, kind, symbol_line, column_no, scope_start,
                        scope_end, signature, detail, local, symbol_file
                    ) = row

                    if prefix_cf and not name.casefold().startswith(prefix_cf):
                        continue

                    is_local = bool(local)
                    if is_local:
                        if symbol_file != file_path:
                            continue
                        if line is None or symbol_line > line or not (
                            scope_start <= line <= scope_end
                        ):
                            continue

                    # Local parameters/variables get priority in the completion list.
                    priority = 0
                    if symbol_file == file_path:
                        priority += 100
                    if is_local:
                        priority += 500
                        # Prefer the most specific lexical scope when local
                        # variables shadow an outer variable with the same name.
                        scope_width = max(0, int(scope_end) - int(scope_start))
                        priority += max(0, 1000 - min(scope_width, 1000))
                    if kind in ("function", "native", "stock", "public", "hook", "command"):
                        priority += 20
                    if current_function and symbol_line >= current_function[0]:
                        priority += 5

                    current = result_by_name.get(name.casefold())
                    item = {
                        "name": name,
                        "kind": kind,
                        "line": symbol_line,
                        "column": column_no,
                        "scope_start": scope_start,
                        "scope_end": scope_end,
                        "signature": signature,
                        "detail": detail,
                        "file": symbol_file,
                        "_priority": priority,
                    }
                    if current is None or priority > current["_priority"]:
                        result_by_name[name.casefold()] = item

                result = list(result_by_name.values())
                result.sort(
                    key=lambda item: (
                        not item["name"].casefold().startswith(prefix_cf),
                        -int(item["_priority"]),
                        item["name"].casefold(),
                    )
                )
                for item in result:
                    item.pop("_priority", None)
                return result

    @staticmethod
    def _current_function_rows(
        db: sqlite3.Connection,
        file_path: str,
        line: int,
    ) -> Optional[Tuple[int, int]]:
        row = db.execute(
            """
            SELECT scope_start, scope_end
            FROM symbols
            WHERE file_id=(SELECT id FROM files WHERE path=?)
              AND kind IN ('function','public','stock','hook','command')
              AND scope_start <= ?
              AND scope_end >= ?
            ORDER BY (scope_end - scope_start) ASC
            LIMIT 1
            """,
            (file_path, line, line),
        ).fetchone()
        if row:
            return int(row[0]), int(row[1])
        return None

    def get_symbol(self, file_path: str, line: int, name: str) -> Optional[Dict[str, object]]:
        if not self.ready:
            return None
        file_path = PawnSourceTools.normalized(file_path)
        with self._lock:
            with self._open_db() as db:
                row = db.execute(
                    """
                    SELECT s.name, s.kind, s.line, s.column_no, s.scope_start,
                           s.scope_end, s.signature, s.detail, f.path
                    FROM symbols s
                    JOIN files f ON f.id=s.file_id
                    WHERE lower(s.name)=lower(?)
                      AND s.file_id=(SELECT id FROM files WHERE path=?)
                    ORDER BY abs(s.line-?)
                    LIMIT 1
                    """,
                    (name, file_path, line),
                ).fetchone()
                if not row:
                    return None
                return {
                    "name": row[0],
                    "kind": row[1],
                    "line": row[2],
                    "column": row[3],
                    "scope_start": row[4],
                    "scope_end": row[5],
                    "signature": row[6],
                    "detail": row[7],
                    "file": row[8],
                }
