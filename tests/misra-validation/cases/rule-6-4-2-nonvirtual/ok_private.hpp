// Near miss (private): a function of a privately inherited base may be concealed; users of the derived class
// cannot reach the base function anyway.
#ifndef KV_RULE_6_4_2_NONVIRTUAL_OK_PRIVATE_HPP
#define KV_RULE_6_4_2_NONVIRTUAL_OK_PRIVATE_HPP

#include <cstdint>

namespace kv::rule_6_4_2_nonvirtual::priv {

class Device {
 public:
  std::int32_t level() const { return 1; }
};

class Sensor : private Device {
 public:
  std::int32_t level(std::int32_t bias) const { return Device::level() + bias; }
};

inline std::int32_t use(Sensor const& s) { return s.level(2); }

}  // namespace kv::rule_6_4_2_nonvirtual::priv

#endif  // KV_RULE_6_4_2_NONVIRTUAL_OK_PRIVATE_HPP
