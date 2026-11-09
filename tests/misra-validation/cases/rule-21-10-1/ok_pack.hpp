// Compliant near miss: a variadic template with a fold expression; the arguments keep their types.
#ifndef KV_RULE_21_10_1_OK_PACK_HPP
#define KV_RULE_21_10_1_OK_PACK_HPP

#include <cstdint>

namespace kv::rule_21_10_1::ok_pack {

template <typename... Masks>
[[nodiscard]] std::uint32_t combine(Masks... masks) {
  return (0U | ... | masks);
}

[[nodiscard]] inline std::uint32_t both(std::uint32_t a, std::uint32_t b) { return combine(a, b); }

}  // namespace kv::rule_21_10_1::ok_pack

#endif  // KV_RULE_21_10_1_OK_PACK_HPP
