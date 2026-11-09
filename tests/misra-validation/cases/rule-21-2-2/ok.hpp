// Compliant: std::string_view knows its length; no C string function is called.
#ifndef KV_RULE_21_2_2_OK_HPP
#define KV_RULE_21_2_2_OK_HPP

#include <cstddef>
#include <string_view>

namespace kv::rule_21_2_2::ok {

[[nodiscard]] inline std::size_t length(std::string_view text) { return text.size(); }

[[nodiscard]] inline bool starts_with_hash(std::string_view text) { return text.starts_with('#'); }

}  // namespace kv::rule_21_2_2::ok

#endif  // KV_RULE_21_2_2_OK_HPP
