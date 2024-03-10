class SignalHandler:
    def __init__(self, successor=None):
        self.successor = successor

    def handle_request(self, data):
        msgs = []
        is_bull, msg = self.do_handle_request(data)
        msgs.extend(msg)
        if self.successor is not None:
            sub_is_bull, sub_msg = self.successor.handle_request(data)
            msgs.extend(sub_msg)
            return is_bull or sub_is_bull, msgs
        else:
            return is_bull, msgs

    def do_handle_request(self, data):
        is_bull = False
        msg = []
        return is_bull, msg


class GradeHandler(SignalHandler):
    def do_handle_request(self, data):
        print("Acheck")
        if data >= 90:
            msg = "成绩等级为：A"
            is_bull = True
        else:
            msg = "分数未大于90"
            is_bull = False
        return is_bull, msg


class GradeBHandler(SignalHandler):
    def do_handle_request(self, data):
        print("Bcheck")
        if 80 <= data < 90:
            msg = "成绩等级为：B"
            is_bull = True
        else:
            msg = "分数小于90大于80"
            is_bull = False
        return is_bull, msg


class GradeCHandler(SignalHandler):
    def do_handle_request(self, data):
        print("Ccheck")
        if 70 <= data < 80:
            msg = "成绩等级为：C"
            is_bull = True
        else:
            msg = "分数小于80大于70"
            is_bull = False
        return is_bull, msg


# 示例：使用责任链模式进行成绩等级判断
def main():
    # 构建责任链
    handler_chain = GradeHandler(GradeBHandler(GradeCHandler()))

    # 测试数据

    is_bull, msg = handler_chain.handle_request(90)
    print(is_bull)
    print(len(msg))


if __name__ == "__main__":
    main()
