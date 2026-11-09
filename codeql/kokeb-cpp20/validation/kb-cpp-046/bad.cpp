// Seeded violations of KB-CPP-046: Result types the compiler will not force callers to check.
#include <cstdint>

namespace kv::kb_cpp_046::bad {

enum class Error : std::uint8_t { kNone, kBus };

template <typename T>
struct Result {
  T value{};
  Error error{Error::kNone};
};

}  // namespace kv::kb_cpp_046::bad

namespace kv::kb_cpp_046::bad_plain {

struct Result {
  bool ok{true};
};

}  // namespace kv::kb_cpp_046::bad_plain
