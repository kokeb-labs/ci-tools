// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_THROW_SPEC_OK_NEAR_HPP
#define KV_RULE_4_1_2_THROW_SPEC_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_2_throw_spec::near {

struct Codec {
  [[nodiscard]] std::uint32_t decode(std::uint32_t v) const noexcept { return v; }
  [[nodiscard]] std::uint32_t encode(std::uint32_t v) const noexcept(true) { return v; }
};

}  // namespace kv::rule_4_1_2_throw_spec::near

#endif  // KV_RULE_4_1_2_THROW_SPEC_OK_NEAR_HPP
