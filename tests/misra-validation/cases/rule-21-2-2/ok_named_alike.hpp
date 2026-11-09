// Compliant near misses: our own functions whose names start like the C string functions.
#ifndef KV_RULE_21_2_2_OK_NAMED_ALIKE_HPP
#define KV_RULE_21_2_2_OK_NAMED_ALIKE_HPP

#include <cstddef>
#include <string>
#include <string_view>

namespace kv::rule_21_2_2::ok_named_alike {

[[nodiscard]] inline std::string_view strip(std::string_view text) {
  while (text.starts_with(' ')) {
    text.remove_prefix(1U);
  }
  return text;
}

[[nodiscard]] inline std::size_t length_of(std::string_view text) {
  return std::char_traits<char>::length(strip(text).data());
}

}  // namespace kv::rule_21_2_2::ok_named_alike

#endif  // KV_RULE_21_2_2_OK_NAMED_ALIKE_HPP
