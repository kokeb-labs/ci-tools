// Compliant: the digit test looks the character up in the set the protocol allows.
#ifndef KV_RULE_24_5_1_OK_HPP
#define KV_RULE_24_5_1_OK_HPP

#include <string_view>

namespace kv::rule_24_5_1::ok {

[[nodiscard]] inline bool is_digit(char c) { return std::string_view{"0123456789"}.find(c) != std::string_view::npos; }

}  // namespace kv::rule_24_5_1::ok

#endif  // KV_RULE_24_5_1_OK_HPP
