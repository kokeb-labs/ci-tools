// Compliant: values arrive as parameters; no function with a static result buffer is called.
#ifndef KV_RULE_25_5_3_OK_HPP
#define KV_RULE_25_5_3_OK_HPP

#include <string_view>

namespace kv::rule_25_5_3::ok {

[[nodiscard]] inline bool same_value(std::string_view first, std::string_view second) { return first == second; }

}  // namespace kv::rule_25_5_3::ok

#endif  // KV_RULE_25_5_3_OK_HPP
