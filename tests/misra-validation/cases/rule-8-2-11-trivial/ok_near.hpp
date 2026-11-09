// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_11_TRIVIAL_OK_NEAR_HPP
#define KV_RULE_8_2_11_TRIVIAL_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_11_trivial::ok_near {

enum class Mode : std::int32_t { kOff, kOn };

std::int32_t take(std::int32_t count, ...);

inline std::int32_t use(std::int32_t const* p) { return take(2, p, Mode::kOn); }

}  // namespace kv::rule_8_2_11_trivial::ok_near

#endif  // KV_RULE_8_2_11_TRIVIAL_OK_NEAR_HPP
