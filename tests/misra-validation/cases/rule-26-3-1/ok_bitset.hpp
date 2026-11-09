// Compliant near miss: std::bitset for packed flags.
#ifndef KV_RULE_26_3_1_OK_BITSET_HPP
#define KV_RULE_26_3_1_OK_BITSET_HPP

#include <bitset>
#include <cstddef>

namespace kv::rule_26_3_1::ok_bitset {

[[nodiscard]] inline std::size_t count_set(const std::bitset<8U>& bits) { return bits.count(); }

}  // namespace kv::rule_26_3_1::ok_bitset

#endif  // KV_RULE_26_3_1_OK_BITSET_HPP
