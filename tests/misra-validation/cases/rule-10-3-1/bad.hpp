// Seeded violation: an anonymous namespace in a header.
#ifndef KV_RULE_10_3_1_BAD_HPP
#define KV_RULE_10_3_1_BAD_HPP

#include <cstdint>

namespace kv::rule_10_3_1::bad {
namespace {

constexpr std::uint32_t kLimit = 8U;

}  // namespace

inline std::uint32_t limit() { return kLimit; }

}  // namespace kv::rule_10_3_1::bad

#endif  // KV_RULE_10_3_1_BAD_HPP
