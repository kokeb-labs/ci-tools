// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_8_2_OK_NEAR_HPP
#define KV_RULE_6_8_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_8_2::near {

// A reference to a caller's object, and a pointer to a member of *this, outlive the call.
inline const std::int32_t& larger(const std::int32_t& a, const std::int32_t& b) { return (a > b) ? a : b; }
class Slot {
 public:
  [[nodiscard]] const std::int32_t* get() const& { return &value_; }
  const std::int32_t* get() const&& = delete;

 private:
  std::int32_t value_{0};
};

}  // namespace kv::rule_6_8_2::near

#endif  // KV_RULE_6_8_2_OK_NEAR_HPP
