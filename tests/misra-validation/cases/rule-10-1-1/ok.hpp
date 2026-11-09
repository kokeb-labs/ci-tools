// Compliant: read-only reference parameters are const; written ones are not.
#ifndef KV_RULE_10_1_1_OK_HPP
#define KV_RULE_10_1_1_OK_HPP

#include <cstdint>

namespace kv::rule_10_1_1::ok {

struct Sample {
  std::uint32_t raw;
};

inline std::uint32_t read_raw(const Sample& s) { return s.raw; }

inline void clear(Sample& s) { s.raw = 0U; }

}  // namespace kv::rule_10_1_1::ok

#endif  // KV_RULE_10_1_1_OK_HPP
