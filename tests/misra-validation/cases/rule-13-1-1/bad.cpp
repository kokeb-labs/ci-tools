// Seeded violation: a class with a virtual base.
#include <cstdint>

namespace kv::rule_13_1_1::bad {

struct Node {
  std::int32_t id = 0;
};

struct Sensor : virtual Node {  // seeded
  std::int32_t value = 0;
};

std::int32_t id_of(const Sensor& s) { return s.id; }

}  // namespace kv::rule_13_1_1::bad
