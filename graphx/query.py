from .pipe import Pipe
from .graph import Graph
from .vertex import Vertex
from .utils import *
from typing import List
import copy


class Query:
    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._initial: List[Vertex] = []

        # pipelines for storing functions, args for storing argument for corresponding function

        self._pipelines: List = []

        self._args = []

    # this does not make sense to be called in the middle way

    def node(self, value):
        if len(self._initial) > 0:
            raise RuntimeError("cannot call node in the midway of a chaining query")
        self._initial.append(self._graph.vertex(value))
        return self

    def clean(self) -> None:
        self._initial.clear()
        self._args.clear()

    def _query(self, name, *args) -> None:
        if len(self._initial) == 0:
            raise RuntimeError("cannot query if didn't call node(val) first")

        pipeline = Pipe(name)
        pipefunc = pipeline.function()

        arguments = [] if len(args) == 0 else list(args)
        self._pipelines.append(pipefunc)
        self._args.append(arguments)

    def run(self):
        if len(self._initial) == 0:
            raise RuntimeError("cannot query if didn't call node(val) first")

        inputs, outputs = self._initial, None

        for i in range(0, len(self._pipelines)):
            pipefunc = self._pipelines[i]

            args = self._args[i]

            if len(args) == 0:
                outputs = pipefunc(inputs)
            else:
                outputs = pipefunc(inputs, *args)

            inputs = outputs
        results = []
        for vertex in outputs:
            results.append(copy.copy(vertex.values()))

        self.clean()
        return results

    # does not make sense to call if didn't call node first

    def forward(self, **kwargs):
        if len(kwargs) > 1:
            raise ValueError("invalid number of kwargs")

        query = decide_query(kwargs)
        name = kwargs.get(query, None)
        self._query("forward", query, name)
        return self

    def backward(self, **kwargs):
        if len(kwargs) > 1:
            raise ValueError("invalid number of kwargs")
        query = decide_query(kwargs)
        name = kwargs.get(query, None)
        self._query("backward", query, name)
        return self

    def unique(self):
        self._query("unique")
        return self

    def take(self, num: int):
        self._query("take", num)
        return self
