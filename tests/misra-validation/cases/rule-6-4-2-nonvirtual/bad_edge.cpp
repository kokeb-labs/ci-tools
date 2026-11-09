// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_4_2_nonvirtual::bad_edge {

class Device {
 public:
  void reset() {}
  void reset(std::int32_t) {}
};
class Sensor : public Device {
 public:
  void reset(std::int32_t, std::int32_t) {}  // hides both inherited overloads
};
void use(Sensor& s) { s.reset(1, 2); }

}  // namespace kv::rule_6_4_2_nonvirtual::bad_edge
