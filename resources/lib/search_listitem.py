from codequick import Route, Resolver, Listitem, run
from codequick.utils import urljoin_partial, bold
# Package imports
from codequick.route import Route
from codequick.script import Script
from codequick.support import auto_sort, build_path, logger_id, dispatcher, CallbackRef
from codequick.utils import ensure_unicode, ensure_native_str, unicode_type, PY3, bold
from codequick import localized

class search_listitem(Listitem):
    @classmethod
    def play_history(cls, callback, name, *args, **kwargs):
        """
        Constructor to add "saved search" support to add-on.

        This will first link to a "sub" folder that lists all saved "search terms". From here,
        "search terms" can be created or removed. When a selection is made, the "callback" function
        that was given will be executed with all parameters forwarded on. Except with one extra
        parameter, ``search_query``, which is the "search term" that was selected.

        :param Callback callback: Function that will be called when the "listitem" is activated.
        :param args: "Positional" arguments that will be passed to the callback.
        :param kwargs: "Keyword" arguments that will be passed to the callback.
        """
        if hasattr(callback, "route"):
            route = callback.route
        elif isinstance(callback, CallbackRef):
            route = callback
        else:
            route = dispatcher.get_route(callback)

        kwargs["first_load"] = True
        kwargs["_route"] = route.path

        item = cls()
        item.label = bold(name)
        item.art.global_thumb("search.png")
        item.info["plot"] = Script.localize(localized.SEARCH_PLOT)
        item.set_callback(Route.ref("/resources/lib/play_from_search:saved_searches"), *args, **kwargs)
        return item

    