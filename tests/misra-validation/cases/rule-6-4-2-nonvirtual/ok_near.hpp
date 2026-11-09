// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_4_2_NONVIRTUAL_OK_NEAR_HPP
#define KV_RULE_6_4_2_NONVIRTUAL_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_4_2_nonvirtual::near {

class Device {
 public:
  void reset() { state_ = 0; }
  [[nodiscard]] std::int32_t state() const { return state_; }

 private:
  std::int32_t state_{0};
};
// A new member with a different name hides nothing.
class Sensor : public Device {
 public:
  void reset_with(std::int32_t v) { reset(); last_ = v; }
  [[nodiscard]] std::int32_t last() const { return last_; }

 private:
  std::int32_t last_{0};
};

}  // namespace kv::rule_6_4_2_nonvirtual::near

#endif  // KV_RULE_6_4_2_NONVIRTUAL_OK_NEAR_HPP
