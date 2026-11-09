// Compliant near misses: a const T& template parameter, and auto&& in a range-for (not a parameter).
#ifndef KV_RULE_28_6_2_OK_CONST_REF_HPP
#define KV_RULE_28_6_2_OK_CONST_REF_HPP

#include <array>
#include <cstdint>

namespace kv::rule_28_6_2::ok_const_ref {

struct Payload {
  std::int32_t value;
};

template <typename T>
[[nodiscard]] std::int32_t read(const T& payload) {
  return payload.value;
}

[[nodiscard]] inline std::int32_t total(const std::array<Payload, 2U>& all) {
  std::int32_t sum = 0;
  for (auto&& p : all) {
    sum = read(p);
  }
  return sum;
}

}  // namespace kv::rule_28_6_2::ok_const_ref

#endif  // KV_RULE_28_6_2_OK_CONST_REF_HPP
