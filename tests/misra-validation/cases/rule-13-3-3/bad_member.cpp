// Seeded violation (member): a member function defined outside its class with renamed parameters.
#include <cstdint>

namespace kv::rule_13_3_3::bad_member {

class Ramp {
 public:
  std::int32_t step(std::int32_t from, std::int32_t to) const;
};

std::int32_t Ramp::step(std::int32_t to, std::int32_t from) const { return to - from; }

}  // namespace kv::rule_13_3_3::bad_member
