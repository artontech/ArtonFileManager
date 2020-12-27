''' default '''

class DefaultModel:
    ''' default model '''

    # page
    page_no = None
    page_size = None

    def none(self):
        ''' clear '''
        self.page_no = None
        self.page_size = None

    def do_page(self) -> bool:
        ''' do page '''
        if self.page_no is None or self.page_size is None:
            return False
        return self.page_no > 0 and self.page_size > 0
