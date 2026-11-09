// Compliant near miss: the object is moved on the last use of each path only.
#ifndef KV_RULE_28_6_3_OK_SCOPED_HPP
#define KV_RULE_28_6_3_OK_SCOPED_HPP

#include <cstddef>
#include <string>
#include <utility>

namespace kv::rule_28_6_3::ok_scoped {

[[nodiscard]] inline std::size_t keep_or_give(bool give, std::string& out) {
  std::string name{"probe"};
  const std::size_t length = name.size();
  if (give) {
    out = std::move(name);
  }
  return length;
}

}  // namespace kv::rule_28_6_3::ok_scoped

#endif  // KV_RULE_28_6_3_OK_SCOPED_HPP
