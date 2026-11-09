// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_3_DEALLOC_MISMATCH_OK_NEAR_HPP
#define KV_RULE_4_1_3_DEALLOC_MISMATCH_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_4_1_3_dealloc_mismatch::near {

// Storage with automatic duration: nothing to deallocate, so nothing to mismatch.
inline std::uint32_t sum(const std::array<std::uint32_t, 4>& a) { return a[0] ^ a[3]; }

}  // namespace kv::rule_4_1_3_dealloc_mismatch::near

#endif  // KV_RULE_4_1_3_DEALLOC_MISMATCH_OK_NEAR_HPP
