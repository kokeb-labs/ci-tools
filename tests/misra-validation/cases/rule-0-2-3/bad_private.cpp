// Seeded violation (private): a private nested type that nothing uses.
#include <cstdint>

namespace kv::rule_0_2_3::bad_private {

class Holder {
 public:
  std::uint32_t get() const { return value_; }

 private:
  struct Spare {  // nothing uses this private type  // seeded
    std::uint32_t v;
  };
  std::uint32_t value_{0U};
};

std::uint32_t read(const Holder& h) { return h.get(); }

}  // namespace kv::rule_0_2_3::bad_private
