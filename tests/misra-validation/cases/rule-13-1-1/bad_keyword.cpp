// Seeded violation (keyword): a virtual base written as public virtual, in a class.
#include <cstdint>

namespace kv::rule_13_1_1::bad_keyword {

class Node {
 public:
  std::int32_t id = 0;
};

class Sensor : public virtual Node {  // seeded
 public:
  std::int32_t value = 0;
};

std::int32_t id_of(const Sensor& s) { return s.id; }

}  // namespace kv::rule_13_1_1::bad_keyword
