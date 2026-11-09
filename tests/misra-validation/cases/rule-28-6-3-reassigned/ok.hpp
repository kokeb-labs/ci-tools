// Compliant: the moved-from object is assigned a new value before it is read again.
#ifndef KV_RULE_28_6_3_REASSIGNED_OK_HPP
#define KV_RULE_28_6_3_REASSIGNED_OK_HPP

#include <cstddef>
#include <string>
#include <utility>

namespace kv::rule_28_6_3_reassigned::ok {

[[nodiscard]] inline bool same_length() {
  std::string first{"sensor"};
  const std::string second = std::move(first);
  first = "probe";
  return first.size() == second.size();
}

}  // namespace kv::rule_28_6_3_reassigned::ok

#endif  // KV_RULE_28_6_3_REASSIGNED_OK_HPP
