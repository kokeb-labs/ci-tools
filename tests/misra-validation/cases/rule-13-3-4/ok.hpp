// Compliant: a pointer to a virtual member is only compared with nullptr.
#ifndef KV_RULE_13_3_4_OK_HPP
#define KV_RULE_13_3_4_OK_HPP

#include <cstdint>

namespace kv::rule_13_3_4::ok {

class Device {
 public:
  Device() = default;
  Device(const Device&) = delete;
  Device(Device&&) = delete;
  Device& operator=(const Device&) = delete;
  Device& operator=(Device&&) = delete;
  virtual ~Device() = default;
  virtual std::uint32_t start() { return 0U; }
};

using Action = std::uint32_t (Device::*)();

inline bool is_set(Action a) { return a != nullptr; }

}  // namespace kv::rule_13_3_4::ok

#endif  // KV_RULE_13_3_4_OK_HPP
