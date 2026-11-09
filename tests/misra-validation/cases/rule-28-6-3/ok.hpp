// Compliant: the moved-from object is not used again.
#ifndef KV_RULE_28_6_3_OK_HPP
#define KV_RULE_28_6_3_OK_HPP

#include <cstddef>
#include <string>
#include <utility>

namespace kv::rule_28_6_3::ok {

[[nodiscard]] inline std::size_t total_length() {
  std::string first{"sensor"};
  const std::string second = std::move(first);
  return second.size();
}

}  // namespace kv::rule_28_6_3::ok

#endif  // KV_RULE_28_6_3_OK_HPP
