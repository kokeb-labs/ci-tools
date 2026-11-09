// Compliant near miss: each strerror result is used up before the next call, and none is stored.
#ifndef KV_RULE_25_5_3_STRERROR_OK_HPP
#define KV_RULE_25_5_3_STRERROR_OK_HPP

#include <cstdint>
#include <cstring>

namespace kv::rule_25_5_3_strerror::ok {

[[nodiscard]] inline bool both_known(std::int32_t a, std::int32_t b) {
  const char* const first = std::strerror(a);
  const bool first_known = first != nullptr;
  const char* const second = std::strerror(b);
  return first_known && (second != nullptr);
}

}  // namespace kv::rule_25_5_3_strerror::ok

#endif  // KV_RULE_25_5_3_STRERROR_OK_HPP
