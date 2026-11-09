// Near miss: a pointer to member function that may be null, tested before the call.
#ifndef KV_RULE_4_1_3_NULL_MEMBER_FUNCTION_POINTER_OK_HPP
#define KV_RULE_4_1_3_NULL_MEMBER_FUNCTION_POINTER_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_3_null_member_function_pointer::ok {

struct Motor {
  [[nodiscard]] std::uint32_t speed() const { return 3U; }
};

using Reading = std::uint32_t (Motor::*)() const;

inline std::uint32_t call_or_zero(const Motor& m, Reading fn) {
  std::uint32_t out = 0U;
  if (fn != nullptr) {
    out = (m.*fn)();
  }
  return out;
}
inline std::uint32_t speed_of(const Motor& m) { return call_or_zero(m, &Motor::speed); }

}  // namespace kv::rule_4_1_3_null_member_function_pointer::ok

#endif  // KV_RULE_4_1_3_NULL_MEMBER_FUNCTION_POINTER_OK_HPP
