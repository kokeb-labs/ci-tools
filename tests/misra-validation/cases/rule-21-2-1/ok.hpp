// Compliant: std::from_chars reports where and whether the conversion failed.
#ifndef KV_RULE_21_2_1_OK_HPP
#define KV_RULE_21_2_1_OK_HPP

#include <charconv>
#include <cstdint>
#include <string_view>
#include <system_error>

namespace kv::rule_21_2_1::ok {

[[nodiscard]] inline bool parse_int(std::string_view text, std::int32_t& out) {
  const std::from_chars_result result = std::from_chars(text.data(), text.data() + text.size(), out);
  return result.ec == std::errc{};
}

}  // namespace kv::rule_21_2_1::ok

#endif  // KV_RULE_21_2_1_OK_HPP
