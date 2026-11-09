// Compliant: the stored lambda lists the variable it captures.
#ifndef KV_RULE_8_1_2_OK_HPP
#define KV_RULE_8_1_2_OK_HPP

#include <cstdint>

namespace kv::rule_8_1_2::ok {

inline std::uint32_t read(std::uint32_t start) {
  std::uint32_t base = start;
  auto f = [base]() { return base; };
  return f();
}

}  // namespace kv::rule_8_1_2::ok

#endif  // KV_RULE_8_1_2_OK_HPP
