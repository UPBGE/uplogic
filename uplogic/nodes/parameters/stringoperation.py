from uplogic.nodes import ULParameterNode


class StringOperationNode(ULParameterNode):
    
    
    def __init__(self):
        ULParameterNode.__init__(self)
        self.string_a = ''
        self.string_b = ''
        self.string_c = ''
        self.zfill_width = 0
        self.operator = 0
        self.RESULT = self.add_output(self.get_result)
        self.operations = [
            self.get_join,
            self.get_split,
            self.get_contains,
            self.get_count,
            self.get_replace,
            self.get_startswith,
            self.get_endswith,
            self.get_upper,
            self.get_lower,
            self.get_zfill
        ]

    def get_result(self):
        return self.operations[self.operator]()

    def get_join(self):
        return str(self.get_input(self.string_a)) + str(self.get_input(self.string_b))

    def get_split(self):
        return str(self.get_input(self.string_a)).split(
            str(self.get_input(self.string_b))
        )

    def get_contains(self):
        return str(self.get_input(self.string_b)) in str(self.get_input(self.string_a))

    def get_count(self):
        return str(self.get_input(self.string_a)).count(
            str(self.get_input(self.string_b))
        )

    def get_replace(self):
        return str(self.get_input(self.string_a)).replace(
            str(self.get_input(self.string_b)),
            str(self.get_input(self.string_c))
        )

    def get_startswith(self):
        return str(self.get_input(self.string_a)).startswith(
            str(self.get_input(self.string_b))
        )

    def get_endswith(self):
        return str(self.get_input(self.string_a)).endswith(
            str(self.get_input(self.string_b))
        )

    def get_upper(self):
        return str(self.get_input(self.string_a)).upper()

    def get_lower(self):
        return str(self.get_input(self.string_a)).lower()

    def get_zfill(self):
        return str(self.get_input(self.string_a)).zfill(
            self.get_input(self.zfill_width)
        )
