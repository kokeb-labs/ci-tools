// Compliant near miss: a protocol class of our own with a member named is_digit.
#ifndef KV_RULE_24_5_1_OK_MEMBER_HPP
#define KV_RULE_24_5_1_OK_MEMBER_HPP

#include <string_view>

namespace kv::rule_24_5_1::ok_member {

struct Protocol {
  [[nodiscard]] bool is_digit(char c) const { return std::string_view{"0123456789"}.find(c) != std::string_view::npos; }
};

[[nodiscard]] inline bool numeric(char c) { return Protocol{}.is_digit(c); }

}  // namespace kv::rule_24_5_1::ok_member

#endif  // KV_RULE_24_5_1_OK_MEMBER_HPP
