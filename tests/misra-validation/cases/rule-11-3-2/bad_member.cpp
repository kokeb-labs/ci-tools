// Seeded violation (member): a class member with three levels of pointer.
#include <cstdint>

namespace kv::rule_11_3_2::bad_member {

struct Graph {
  std::int32_t*** edges = nullptr;  // seeded
};

bool empty(const Graph& g) { return g.edges == nullptr; }

}  // namespace kv::rule_11_3_2::bad_member
