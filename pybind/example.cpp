#include <pybind11/pybind11.h>

namespace py = pybind11;


class Scheduler {
public:
  Scheduler(int agent) {
    set_agent(agent);
  }

  void step() {
    this->agent += 1;
  }

  void set_agent(int agent) {
    this->agent = agent;
  }

  int get_agent() const {
    return agent;
  }

protected:
  int agent;
};

PYBIND11_MODULE(example, m) {
    py::class_<Scheduler>(m, "Scheduler")
        .def(py::init<int>())
        .def("set_agent", &Scheduler::set_agent)
        .def("step", &Scheduler::step)
        .def("get_agent", &Scheduler::get_agent);
}
