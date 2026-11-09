// Compliant by exception 2: a bool result discarded by a cast to void, inside a member function
// template of a class template (the driver shape).
#ifndef KV_RULE_7_0_1_OK_VOID_HPP
#define KV_RULE_7_0_1_OK_VOID_HPP

#include <cstddef>
#include <cstdint>

namespace kv::rule_7_0_1::ok_void {

template <typename Port>
class Bus {
 public:
  explicit Bus(Port& port) noexcept : port_{port} {}

  template <std::size_t N>
  std::int32_t send() noexcept {
    if (!port_.Set(false)) {
      (void)port_.Set(true);  // best effort to restore the idle level; its result changes nothing
      return 1;
    }
    return static_cast<std::int32_t>(N);
  }

 private:
  Port& port_;
};

struct FakePort {
  bool Set(bool level) noexcept { return level; }
};

inline std::int32_t run() noexcept {
  FakePort port{};
  Bus<FakePort> bus{port};
  return bus.send<4U>();
}

}  // namespace kv::rule_7_0_1::ok_void

#endif  // KV_RULE_7_0_1_OK_VOID_HPP
