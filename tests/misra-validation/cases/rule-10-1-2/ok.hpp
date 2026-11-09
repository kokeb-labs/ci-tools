// Compliant: volatile only on the object that models a memory-mapped register.
#ifndef KV_RULE_10_1_2_OK_HPP
#define KV_RULE_10_1_2_OK_HPP

#include <cstdint>

namespace kv::rule_10_1_2::ok {

struct Registers {
  volatile std::uint32_t status;
};

inline std::uint32_t read_status(const Registers& regs) { return regs.status; }

}  // namespace kv::rule_10_1_2::ok

#endif  // KV_RULE_10_1_2_OK_HPP
