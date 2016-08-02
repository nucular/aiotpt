routes = []

from .views.Startup import StartupEndpoint
routes.append(("*", "/Startup.json", StartupEndpoint))
from .views.Stats import StatsEndpoint
routes.append(("*", "/Stats.json", StatsEndpoint))

from .views.Register import RegisterEndpoint
routes.append(("*", "/Register.json", RegisterEndpoint))
from .views.Login import LoginEndpoint
routes.append(("*", "/Login.json", LoginEndpoint))

from .views.User import UserEndpoint
routes.append(("*", "/User.json", UserEndpoint))
from .views.Save import SaveEndpoint
routes.append(("*", "/Save.api", SaveEndpoint))
from .views.Vote import VoteEndpoint
routes.append(("*", "/Vote.api", VoteEndpoint))

from .views.Browse import BrowseEndpoint
routes.append(("*", "/Browse.json", BrowseEndpoint))
from .views.Browse.Comments import CommentsEndpoint
routes.append(("*", "/Browse/Comments.json", CommentsEndpoint))
from .views.Browse.Tags import TagsEndpoint
routes.append(("*", "/Browse/Tags.json", TagsEndpoint))
from .views.Browse.EditTag import EditTagEndpoint
routes.append(("*", "/Browse/EditTag.json", EditTagEndpoint))
from .views.Browse.Favourite import FavouriteEndpoint
routes.append(("*", "/Browse/Favourite.json", FavouriteEndpoint))
from .views.Browse.Delete import DeleteEndpoint
routes.append(("*", "/Browse/Delete.json", DeleteEndpoint))
from .views.Browse.View import ViewEndpoint
routes.append(("*", "/Browse/View.json", ViewEndpoint))

from .views.Static import StaticEndpoint
routes.append(("GET", "/{id:[0-9]+}.{ext:cps}", StaticEndpoint))
routes.append(("GET", "/{id:[0-9]+}_{size:large|small}.{ext:png|pti}", StaticEndpoint))
