// Seeded violation: an unnamed namespace at the top level of a header.
#ifndef KV_RULE_10_3_1_BAD_HPP
#define KV_RULE_10_3_1_BAD_HPP

#include <cstdint>

namespace {  // seeded

constexpr std::uint32_t kRule1031Limit = 8U;

}  // namespace

namespace kv::rule_10_3_1::bad {

inline std::uint32_t limit() { return kRule1031Limit; }

}  // namespace kv::rule_10_3_1::bad

#endif  // KV_RULE_10_3_1_BAD_HPP
