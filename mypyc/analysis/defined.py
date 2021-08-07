from typing import Tuple, Set

from mypyc.ir.ops import (
    OpVisitor, Register, Goto, Assign, AssignMulti, SetMem, Call, MethodCall, LoadErrorValue,
    LoadLiteral, GetAttr, SetAttr, LoadStatic, InitStatic, TupleGet, TupleSet, Box, Unbox,
    Cast, RaiseStandardError, CallC, Truncate, LoadGlobal, IntOp, ComparisonOp, LoadMem,
    GetElementPtr, LoadAddress, KeepAlive, Branch, Return, Unreachable, RegisterOp
)

GenAndKill = Tuple[Set[None], Set[None]]

CLEAN: GenAndKill = set(), set()
DIRTY: GenAndKill = {None}, {None}


class ArbitraryExecutionVisitor(OpVisitor[GenAndKill]):
    """Analyze whether arbitrary code may have been executed at certain point.

    More formally, the set is not empty if along some path from IR entry point
    arbitrary code could have been executed.
    """

    def __init__(self, self_reg: Register) -> None:
        self.self_reg = self_reg

    def visit_goto(self, op: Goto) -> GenAndKill:
        return CLEAN

    def visit_branch(self, op: Branch) -> GenAndKill:
        return CLEAN

    def visit_return(self, op: Return) -> GenAndKill:
        return DIRTY

    def visit_unreachable(self, op: Unreachable) -> GenAndKill:
        # TODO
        return DIRTY

    def visit_assign(self, op: Assign) -> GenAndKill:
        # TODO: what if target is self?
        return CLEAN if op.src is not self.self_reg else DIRTY

    def visit_assign_multi(self, op: AssignMulti) -> GenAndKill:
        return CLEAN

    def visit_set_mem(self, op: SetMem) -> GenAndKill:
        return CLEAN

    def visit_call(self, op: Call) -> GenAndKill:
        return DIRTY

    def visit_method_call(self, op: MethodCall) -> GenAndKill:
        return DIRTY

    def visit_load_error_value(self, op: LoadErrorValue) -> GenAndKill:
        return CLEAN

    def visit_load_literal(self, op: LoadLiteral) -> GenAndKill:
        return CLEAN

    def visit_get_attr(self, op: GetAttr) -> GenAndKill:
        cl = op.class_type.class_ir
        if cl.get_method(op.attr):
            # Property -- calls a function
            return DIRTY
        return CLEAN

    def visit_set_attr(self, op: SetAttr) -> GenAndKill:
        cl = op.class_type.class_ir
        if cl.get_method(op.attr):
            # Property - calls a function
            return DIRTY
        return CLEAN

    def visit_load_static(self, op: LoadStatic) -> GenAndKill:
        return CLEAN

    def visit_init_static(self, op: InitStatic) -> GenAndKill:
        return self.check_register_op(op)

    def visit_tuple_get(self, op: TupleGet) -> GenAndKill:
        return CLEAN

    def visit_tuple_set(self, op: TupleSet) -> GenAndKill:
        return self.check_register_op(op)

    def visit_box(self, op: Box) -> GenAndKill:
        return self.check_register_op(op)

    def visit_unbox(self, op: Unbox) -> GenAndKill:
        return self.check_register_op(op)

    def visit_cast(self, op: Cast) -> GenAndKill:
        return self.check_register_op(op)

    def visit_raise_standard_error(self, op: RaiseStandardError) -> GenAndKill:
        return CLEAN

    def visit_call_c(self, op: CallC) -> GenAndKill:
        # TODO: Whitelist certain functions
        return DIRTY

    def visit_truncate(self, op: Truncate) -> GenAndKill:
        return CLEAN

    def visit_load_global(self, op: LoadGlobal) -> GenAndKill:
        return CLEAN

    def visit_int_op(self, op: IntOp) -> GenAndKill:
        return CLEAN

    def visit_comparison_op(self, op: ComparisonOp) -> GenAndKill:
        return CLEAN

    def visit_load_mem(self, op: LoadMem) -> GenAndKill:
        return CLEAN

    def visit_get_element_ptr(self, op: GetElementPtr) -> GenAndKill:
        return CLEAN

    def visit_load_address(self, op: LoadAddress) -> GenAndKill:
        return CLEAN

    def visit_keep_alive(self, op: KeepAlive) -> GenAndKill:
        return CLEAN

    def check_register_op(self, op: RegisterOp) -> GenAndKill:
        if any(src is self.self_reg for src in op.sources()):
            return DIRTY
        return CLEAN
