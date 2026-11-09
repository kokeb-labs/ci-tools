// Compliant: each result is used up before the next call, and none is stored in an object.
#ifndef KV_RULE_25_5_3_ORDERED_USE_OK_HPP
#define KV_RULE_25_5_3_ORDERED_USE_OK_HPP

#include <cstdlib>

namespace kv::rule_25_5_3_ordered_use::ok {

[[nodiscard]] inline bool both_set() {
  const char* const first = std::getenv("FIRST");
  const bool has_first = first != nullptr;
  const char* const second = std::getenv("SECOND");
  return has_first && (second != nullptr);
}

}  // namespace kv::rule_25_5_3_ordered_use::ok

#endif  // KV_RULE_25_5_3_ORDERED_USE_OK_HPP
