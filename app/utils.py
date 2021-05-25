def get_component(tag_subtree, selector, attribute = None, return_list = False):
        try:
            if attribute:
                return tag_subtree.select(selector).pop(0)[attribute].strip()
            if return_list:
                return [item.get_text().strip() for item in tag_subtree.select(selector)]
            return tag_subtree.select(selector).pop(0).get_text().strip()
        except IndexError:
            return None