from .bing import Bing
from .duckduckgo import Duckduckgo
from .google import Google
from .brave import Brave
from .sougou import Sougou
from .baidu import Baidu

search_engines_dict = {
    'google': Google,
    'bing': Bing,
    'duckduckgo': Duckduckgo,
    'brave': Brave,
    'sougou': Sougou,
    'baidu': Baidu
}