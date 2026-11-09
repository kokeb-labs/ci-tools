// Compliant near miss: a parser of our own whose member is named atoi; it reports failure.
#ifndef KV_RULE_21_2_1_OK_MEMBER_HPP
#define KV_RULE_21_2_1_OK_MEMBER_HPP

#include <charconv>
#include <cstdint>
#include <string_view>
#include <system_error>

namespace kv::rule_21_2_1::ok_member {

struct Parser {
  [[nodiscard]] bool atoi(std::string_view text, std::int32_t& out) const {
    const std::from_chars_result result = std::from_chars(text.data(), text.data() + text.size(), out);
    return result.ec == std::errc{};
  }
};

[[nodiscard]] inline bool parse(std::string_view text, std::int32_t& out) { return Parser{}.atoi(text, out); }

}  // namespace kv::rule_21_2_1::ok_member

#endif  // KV_RULE_21_2_1_OK_MEMBER_HPP
