from selenium import webdriver


def get_index():
    url = 'https://shanghai.anjuke.com/community/?from=navigation'
    dr =webdriver.PhantomJS()
    dr.get(url)
    print(dr.page_source)


if __name__ == '__main__':
    get_index()
