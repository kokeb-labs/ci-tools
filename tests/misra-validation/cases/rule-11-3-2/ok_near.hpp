// Near misses (near): two levels of pointer, the most allowed.
#ifndef KV_RULE_11_3_2_OK_NEAR_HPP
#define KV_RULE_11_3_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_11_3_2::ok_near {

inline std::uint32_t chase(const std::uint32_t* const* pp) { return **pp; }

inline void clear(std::uint32_t** pp) { **pp = 0U; }

}  // namespace kv::rule_11_3_2::ok_near

#endif  // KV_RULE_11_3_2_OK_NEAR_HPP
