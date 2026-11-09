// Compliant: configuration arrives as a parameter; no environment or locale function is called.
#ifndef KV_RULE_25_5_2_OK_HPP
#define KV_RULE_25_5_2_OK_HPP

#include <string_view>

namespace kv::rule_25_5_2::ok {

[[nodiscard]] inline bool has_home(std::string_view home) { return !home.empty(); }

}  // namespace kv::rule_25_5_2::ok

#endif  // KV_RULE_25_5_2_OK_HPP
