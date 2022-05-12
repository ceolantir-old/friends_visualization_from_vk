from typing import NamedTuple, Union, List, Any, Dict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import requests
from networkx import Graph


class GraphVertices(NamedTuple):
    quantity: str
    average_cluster_coefficient: str
    average_degree: str


class VkFriendsVisualization:
    def __init__(self, vk_access_token: str, central_user_id: str):
        self._vk_access_token = vk_access_token
        self._central_user_id = central_user_id

        self._central_users = self._get_central_users()

    def _get_friends(self, user_id: str = None, with_name: bool = False) -> Union[List[Any], Any]:
        if not user_id:
            user_id = self._central_user_id

        fields = 'first_name,last_name' if with_name else ''
        url = f'https://api.vk.com/method/friends.get?' \
              f'access_token={self._vk_access_token}&' \
              f'user_id={user_id}&' \
              f'fields={fields}&' \
              f'v=5.131'
        response = requests.get(url).json()

        if response.get('error'):
            print(response.get('error'))
            return []

        return response.get('response').get('items')

    def _get_central_users(self) -> Dict[str, str]:
        central_users = self._get_friends(with_name=True)
        central_users_dict = {
            user_dict['id']: user_dict.get('first_name') + ' ' + user_dict.get('last_name')
            for user_dict in central_users
        }

        central_users_dict[self._central_user_id] = 'Я'

        return central_users_dict

    def _get_graph(self) -> Graph:
        graph_data = {}

        for user_id in self._central_users.keys():
            graph_data[user_id] = self._get_friends(user_id)

        graph = nx.Graph()
        for user_id, user_friends in graph_data.items():
            graph.add_node(self._central_users[user_id])
            for friend_id in user_friends:
                if friend_id in self._central_users:
                    graph.add_edge(self._central_users[user_id], self._central_users[friend_id])

        return graph

    def _graph_save(self, graph, picture_name, with_labels=False, **kwargs):
        plt.figure(figsize=(60, 45))
        nx.draw_kamada_kawai(graph, with_labels=with_labels, node_size=1000, width=1.5, **kwargs)
        plt.savefig(picture_name)

    def _get_graph_descr(self, graph):
        return GraphVertices(
            graph.number_of_nodes(),
            np.average(np.array(list(nx.clustering(graph).values()))),
            np.average(np.array([degree for user_name_, degree in nx.degree(graph)]))
        )

    def graph_plot_with_central_vertex(self) -> GraphVertices:
        graph = self._get_graph()

        self._graph_save(graph, 'my_friends_with_central_vertex.png')
        # self._graph_save(
        #     graph,
        #     'my_friends_with_central_vertex_labeled.png',
        #     with_labels=True,
        #     font_size=25,
        #     font_color='red',
        # )

        return self._get_graph_descr(graph)

    def graph_plot_without_central_vertex(self) -> GraphVertices:
        graph = self._get_graph()

        graph.remove_node(self._central_users[self._central_user_id])

        self._graph_save(graph, 'my_friends_without_central_vertex.png')
        # self._graph_save(
        #     graph,
        #     'my_friends_without_central_vertex_labeled.png',
        #     with_labels=True,
        #     font_size=25,
        #     font_color='red',
        # )

        return self._get_graph_descr(graph)


if __name__ == "__main__":
    vk_access_token = ''
    central_user_id = ''
    vk_frineds_visualization = VkFriendsVisualization(vk_access_token, central_user_id)

    print(vk_frineds_visualization.graph_plot_with_central_vertex())
    print(vk_frineds_visualization.graph_plot_without_central_vertex())
