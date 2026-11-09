// Compliant near miss: a table of our own called a jump table; control flow stays structured.
#ifndef KV_RULE_21_10_2_OK_NAMED_ALIKE_HPP
#define KV_RULE_21_10_2_OK_NAMED_ALIKE_HPP

#include <array>
#include <cstdint>

namespace kv::rule_21_10_2::ok_named_alike {

using Handler = std::uint32_t (*)(std::uint32_t);

[[nodiscard]] inline std::uint32_t flip(std::uint32_t v) { return v ^ 1U; }

[[nodiscard]] inline std::uint32_t jump(bool first, std::uint32_t v) {
  const std::array<Handler, 1U> jump_table{&flip};
  return first ? jump_table[0](v) : v;
}

}  // namespace kv::rule_21_10_2::ok_named_alike

#endif  // KV_RULE_21_10_2_OK_NAMED_ALIKE_HPP
