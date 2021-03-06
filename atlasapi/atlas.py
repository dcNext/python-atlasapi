# Copyright (c) 2018 Yellow Pages Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Atlas module

Core module which provides access to MongoDB Atlas Cloud Provider APIs
"""

from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta

from .errors import *
from .network import Network
from .settings import Settings


class Atlas:
    """Atlas constructor

    Args:
        user (str): Atlas user
        password (str): Atlas password
        group (str): Atlas group
    """

    def __init__(self, user, password, group):
        self.group = group

        # Network calls which will handld user/passord for auth
        self.network = Network(user, password)

        # APIs
        self.Clusters = Atlas._Clusters(self)
        self.Whitelist = Atlas._Whitelist(self)
        self.DatabaseUsers = Atlas._DatabaseUsers(self)
        self.Projects = Atlas._Projects(self)
        self.Alerts = Atlas._Alerts(self)

    class _Clusters:
        """Clusters API

        see: https://docs.atlas.mongodb.com/reference/api/clusters/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def is_existing_cluster(self, cluster):
            """Check if the cluster exists

            Not part of Atlas api but provided to simplify some code

            Args:
                cluster (str): The cluster name

            Returns:
                bool: The cluster exists or not
            """

            try:
                self.get_a_single_cluster(cluster)
                return True
            except ErrAtlasNotFound:
                return False

        def get_all_clusters(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Clusters

            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-all/

            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return ClustersGetAll(self.atlas, pageNum, itemsPerPage)

            uri = Settings.api_resources["Clusters"]["Get All Clusters"] % (
                self.atlas.group, pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_a_single_cluster(self, cluster):
            """Get a Single Cluster

            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-one/

            Args:
                cluster (str): The cluster name

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Clusters"]["Get a Single Cluster"] % (
                self.atlas.group, cluster)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def delete_a_cluster(self, cluster, areYouSure=False):
            """Delete a Cluster

            url: https://docs.atlas.mongodb.com/reference/api/clusters-delete-one/

            Args:
                cluster (str): Cluster name

            Keyword Args:
                areYouSure (bool): safe flag to don't delete a cluster by mistake

            Returns:
                dict: Response payload

            Raises:
                ErrConfirmationRequested: Need a confirmation to delete the cluster
            """
            if areYouSure:
                uri = Settings.api_resources["Clusters"]["Delete a Cluster"] % (
                    self.atlas.group, cluster)
                return self.atlas.network.delete(Settings.BASE_URL + uri)
            else:
                raise ErrConfirmationRequested(
                    "Please set areYouSure=True on delete_a_cluster call if you really want to delete [%s]" % cluster)

    class _Whitelist:
        """Whitelist API

        see: https://docs.atlas.mongodb.com/reference/api/whitelist/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_all_whitelist_entries(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All whitelist entries

            url: https://docs.atlas.mongodb.com/reference/api/whitelist-get-all/

            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return WhitelistGetAll(self.atlas, pageNum, itemsPerPage)

            uri = Settings.api_resources["Whitelist"]["Get All Whitelist Entries"] % (
                self.atlas.group, pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_whitelist_entry(self, ip_address):
            """Get a whitelist entry

            url: https://docs.atlas.mongodb.com/reference/api/whitelist-get-one-entry/

            Args:
                ip_address (str): ip address to fetch from whitelist

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Whitelist"]["Get Whitelist Entry"] % (
                self.atlas.group, ip_address)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def create_whitelist_entry(self, ip_address, comment):
            """Create a whitelist entry

            url: https://docs.atlas.mongodb.com/reference/api/whitelist-add-one/

            Args:
                ip_address (str): ip address to add to whitelist
                comment (str): comment describing the whitelist entry

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Whitelist"]["Create Whitelist Entry"] % self.atlas.group

            whitelist_entry = [{'ipAddress': ip_address, 'comment': comment}]
            return self.atlas.network.post(Settings.BASE_URL + uri, whitelist_entry)

        def delete_a_whitelist_entry(self, ip_address):
            """Delete a whitelist entry

            url: https://docs.atlas.mongodb.com/reference/api/whitelist-delete-one/

            Args:
                ip_address (str): ip address to delete from whitelist

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Whitelist"]["Delete Whitelist Entry"] % (
                self.atlas.group, ip_address)
            return self.atlas.network.delete(Settings.BASE_URL + uri)

    class _DatabaseUsers:
        """Database Users API

        see: https://docs.atlas.mongodb.com/reference/api/database-users/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_all_database_users(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Database Users

            url: https://docs.atlas.mongodb.com/reference/api/database-users-get-all-users/

            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return DatabaseUsersGetAll(self.atlas, pageNum, itemsPerPage)

            uri = Settings.api_resources["Database Users"]["Get All Database Users"] % (
                self.atlas.group, pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_a_single_database_user(self, user):
            """Get a Database User

            url: https://docs.atlas.mongodb.com/reference/api/database-users-get-single-user/

            Args:
                user (str): User

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Get a Single Database User"] % (
                self.atlas.group, user)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def create_a_database_user(self, permissions):
            """Create a Database User

            url: https://docs.atlas.mongodb.com/reference/api/database-users-create-a-user/

            Args:
                permissions (DatabaseUsersPermissionsSpec): Permissions to apply

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Create a Database User"] % self.atlas.group
            return self.atlas.network.post(Settings.BASE_URL + uri, permissions.getSpecs())

        def update_a_database_user(self, user, permissions):
            """Update a Database User

            url: https://docs.atlas.mongodb.com/reference/api/database-users-update-a-user/

            Args:
                user (str): User
                permissions (DatabaseUsersUpdatePermissionsSpecs): Permissions to apply

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Update a Database User"] % (
                self.atlas.group, user)
            return self.atlas.network.patch(Settings.BASE_URL + uri, permissions.getSpecs())

        def delete_a_database_user(self, user):
            """Delete a Database User

            url: https://docs.atlas.mongodb.com/reference/api/database-users-delete-a-user/

            Args:
                user (str): User to delete

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Delete a Database User"] % (
                self.atlas.group, user)
            return self.atlas.network.delete(Settings.BASE_URL + uri)

    class _Projects:
        """Projects API

        see: https://docs.atlas.mongodb.com/reference/api/projects/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_all_projects(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Projects

            url: https://docs.atlas.mongodb.com/reference/api/project-get-all/

            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return ProjectsGetAll(self.atlas, pageNum, itemsPerPage)

            uri = Settings.api_resources["Projects"]["Get All Projects"] % (
                pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_one_project(self, groupid):
            """Get one Project

            url: https://docs.atlas.mongodb.com/reference/api/project-get-one/

            Args:
                groupid (str): Group Id

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Projects"]["Get One Project"] % (
                groupid)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def create_a_project(self, name, orgId=None):
            """Create a Project

            url: https://docs.atlas.mongodb.com/reference/api/project-create-one/

            Args:
                name (str): Project name

            Keyword Args:
                orgId (ObjectId): The ID of the organization you want to create the project within.

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Projects"]["Create a Project"]

            project = {"name": name}
            if orgId:
                project["orgId"] = orgId

            return self.atlas.network.post(Settings.BASE_URL + uri, project)

    class _Alerts:
        """Alerts API

        see: https://docs.atlas.mongodb.com/reference/api/alerts/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_all_alerts(self, status=None, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Alerts

            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-all-alerts/

            Keyword Args:
                status (AlertStatusSpec): filter on alerts status
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return AlertsGetAll(self.atlas, status, pageNum, itemsPerPage)

            if status:
                uri = Settings.api_resources["Alerts"]["Get All Alerts with status"] % (
                    self.atlas.group, status, pageNum, itemsPerPage)
            else:
                uri = Settings.api_resources["Alerts"]["Get All Alerts"] % (
                    self.atlas.group, pageNum, itemsPerPage)

            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_an_alert(self, alert):
            """Get an Alert 

            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-alert/

            Args:
                alert (str): The alert id

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Alerts"]["Get an Alert"] % (
                self.atlas.group, alert)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def acknowledge_an_alert(self, alert, until, comment=None):
            """Acknowledge an Alert

            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/

            Args:
                alert (str): The alert id
                until (datetime): Acknowledge until

            Keyword Args:
                comment (str): The acknowledge comment

            Returns:
                dict: Response payload
            """

            data = {"acknowledgedUntil": until.isoformat(timespec='seconds')}
            if comment:
                data["acknowledgementComment"] = comment

            uri = Settings.api_resources["Alerts"]["Acknowledge an Alert"] % (
                self.atlas.group, alert)
            return self.atlas.network.patch(Settings.BASE_URL + uri, data)

        def unacknowledge_an_alert(self, alert):
            """Acknowledge an Alert

            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/

            Args:
                alert (str): The alert id

            Returns:
                dict: Response payload
            """

            # see https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/#request-body-parameters
            # To unacknowledge a previously acknowledged alert, set the field value to the past.
            now = datetime.now(timezone.utc)
            until = now - relativedelta(days=1)
            return self.acknowledge_an_alert(alert, until)

        def acknowledge_an_alert_forever(self, alert, comment=None):
            """Acknowledge an Alert forever

            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/

            Args:
                alert (str): The alert id

            Keyword Args:
                comment (str): The acknowledge comment

            Returns:
                dict: Response payload
            """

            # see https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/#request-body-parameters
            # To acknowledge an alert “forever”, set the field value to 100 years in the future.
            now = datetime.now(timezone.utc)
            until = now + relativedelta(years=100)
            return self.acknowledge_an_alert(alert, until, comment)


class AtlasPagination:
    """Atlas Pagination Generic Implementation

    Constructor

    Args:
        atlas (Atlas): Atlas instance
        fetch (function): The function "get_all" to call
        pageNum (int): Page number
        itemsPerPage (int): Number of Users per Page
    """

    def __init__(self, atlas, fetch, pageNum, itemsPerPage):
        self.atlas = atlas
        self.fetch = fetch
        self.pageNum = pageNum
        self.itemsPerPage = itemsPerPage

    def __iter__(self):
        """Iterable

        Yields:
            str: One result
        """

        # pageNum is set with the value requested (so not necessary 1)
        pageNum = self.pageNum
        # total: This is a fake value to enter into the while. It will be updated with a real value later
        total = pageNum * self.itemsPerPage

        while (pageNum * self.itemsPerPage - total < self.itemsPerPage):
            # fetch the API
            try:
                details = self.fetch(pageNum, self.itemsPerPage)
            except:
                raise ErrPagination()

            # set the real total
            total = details["totalCount"]

            # while into the page results
            results = details["results"]
            results_count = len(results)
            index = 0
            while (index < results_count):
                result = results[index]
                index += 1
                yield result

            # next page
            pageNum += 1


class DatabaseUsersGetAll(AtlasPagination):
    """Pagination for Database User : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.DatabaseUsers.get_all_database_users, pageNum, itemsPerPage)


class WhitelistGetAll(AtlasPagination):
    """Pagination for Database User : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.Whitelist.get_all_whitelist_entries, pageNum, itemsPerPage)


class ProjectsGetAll(AtlasPagination):
    """Pagination for Projects : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.Projects.get_all_projects, pageNum, itemsPerPage)


class ClustersGetAll(AtlasPagination):
    """Pagination for Clusters : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.Clusters.get_all_clusters, pageNum, itemsPerPage)


class AlertsGetAll(AtlasPagination):
    """Pagination for Alerts : Get All"""

    def __init__(self, atlas, status, pageNum, itemsPerPage):
        super().__init__(atlas, self.fetch, pageNum, itemsPerPage)
        self.get_all_alerts = atlas.Alerts.get_all_alerts
        self.status = status

    def fetch(self, pageNum, itemsPerPage):
        """Intermediate fetching

        Args:
            pageNum (int): Page number
            itemsPerPage (int): Number of Users per Page

        Returns:
            dict: Response payload
        """
        return self.get_all_alerts(self.status, pageNum, itemsPerPage)
